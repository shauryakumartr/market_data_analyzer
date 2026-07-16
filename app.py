"""Instagram Campaign Analyzer Orchestrator (Streamlit Application)
"""

import streamlit as st
import pandas as pd
import logging

from config.settings import MAPPING_DROPDOWN_OPTIONS
from data.loader import load_csv
from data.filter import filter_data
from mapping.column_mapper import map_columns
from cleaning.data_cleaner import clean_data
from validation.duplicate_validator import validate_no_duplicate_mappings
from validation.validator import run_validation
from analytics.kpi_calculator import calculate_basic_kpis
from analytics.performance import compare_performance
from analytics.segmentation import analyze_segments
from analytics.graph_data import prepare_graph_data
from analytics.anomaly_detector import detect_anomalies
from insights.insight_engine import (
    generate_kpi_summary,
    generate_best_performers,
    generate_performer_insights,
    generate_anomaly_insights,
)
from insights.recommendations import generate_recommendations
from insights.summary_builder import build_ai_summary
from ai.ai_engine import generate_ai_response
from visualization.charts import (
    create_bar_chart,
    create_scatter_chart,
    create_line_chart,
    create_pie_chart,
)

# Setup logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Application Title
st.title('Instagram Campaign Analyzer')

# File Upload
uploaded_file = st.file_uploader("Upload a CSV file of the data", type=["csv"])

if uploaded_file:
    if not uploaded_file.name.endswith(".csv"):
        st.error("Invalid Filetype. Use a CSV file")
        st.stop()

    # Load raw data
    try:
        df_raw = load_csv(uploaded_file)
    except Exception as e:
        logger.exception("Failed to load uploaded file")
        st.error(f"Invalid file format or corrupted file: {e}")
        st.stop()

    # Session State Initialization for mappings
    if "mapping_confirmed" not in st.session_state:
        st.session_state.mapping_confirmed = False

    if not st.session_state.mapping_confirmed:
        predicted_mapping = map_columns(df_raw)
        st.header("Please verify and check the column mapping before proceeding")
        
        user_mapping = {}
        with st.expander("Column Mapping Configurations", expanded=True):
            col_left, col_right = st.columns(2)
            with col_left:
                st.subheader("Your CSV Column")
            with col_right:
                st.subheader("Mapped Canonical Field")

            for column, predicted_alias in predicted_mapping.items():
                with st.container(border=True):
                    c_left, c_right = st.columns(2)
                    with c_left:
                        st.write(column)
                    with c_right:
                        default_idx = (
                            MAPPING_DROPDOWN_OPTIONS.index(predicted_alias)
                            if predicted_alias in MAPPING_DROPDOWN_OPTIONS
                            else 0
                        )
                        user_mapping[column] = st.selectbox(
                            "Select Canonical Field",
                            options=MAPPING_DROPDOWN_OPTIONS,
                            key=f"column_mapper_{column}",
                            index=default_idx,
                            label_visibility="collapsed"
                        )

        if st.button("Confirm Mapping"):
            # Check for duplicate mappings
            dup_report = validate_no_duplicate_mappings(user_mapping)
            if not dup_report['is_valid']:
                st.error(
                    f"Duplicate mappings found for canonical fields: {dup_report['duplicate_mappings']}. "
                    "Each canonical field must be mapped to at most one CSV column."
                )
            else:
                # Store user mapping configurations in session state
                st.session_state.user_mapping = user_mapping
                st.session_state.mapping_confirmed = True
                st.rerun()

    # Analytics View State Management
    if "analytics_view" not in st.session_state:
        st.session_state.analytics_view = False

    if st.session_state.mapping_confirmed and not st.session_state.analytics_view:
        if st.button("Proceed to Analytics"):
            st.session_state.analytics_view = True
            st.rerun()

    if st.session_state.analytics_view:
        # Build mapped dataframe using stored mapping
        user_mapping = st.session_state.user_mapping
        
        # Filter mapping to exclude Ignore Column or None/Custom
        rename_dict = {}
        columns_to_keep = []
        for orig, canonical in user_mapping.items():
            if canonical not in (None, "Ignore Column", "Custom Column"):
                rename_dict[orig] = canonical
                columns_to_keep.append(orig)
        
        df_mapped = df_raw[columns_to_keep].rename(columns=rename_dict)

        # Run Validation Pipeline
        validation_report = run_validation(df_mapped)
        if not validation_report['is_valid']:
            st.error("Uploaded dataset failed schema or structural validation checks. Please review logs.")
            with st.expander("Validation Report Details"):
                st.write(validation_report)
            st.stop()

        # Clean Data
        df_cleaned = clean_data(df_mapped)
        anomalies = detect_anomalies(df_cleaned)

        # Filters Sidebar setup
        st.sidebar.header("Data Selection Filters")
        
        # Guard filters for column existence
        objectives = ["All"]
        if 'objective' in df_cleaned.columns:
            objectives += list(df_cleaned['objective'].dropna().unique())
        campaign_objective_filter = st.sidebar.selectbox("Campaign Objective", options=objectives, key='campaign_filter')

        devices = list(df_cleaned['device'].dropna().unique()) if 'device' in df_cleaned.columns else []
        device_filter = st.sidebar.multiselect("Device", options=devices, default=devices, key='device_filter')

        genders = list(df_cleaned['gender'].dropna().unique()) if 'gender' in df_cleaned.columns else []
        gender_filter = st.sidebar.multiselect("Gender", options=genders, default=genders, key='gender_filter')

        age_groups = list(df_cleaned['age_group'].dropna().unique()) if 'age_group' in df_cleaned.columns else []
        age_group_filter = st.sidebar.multiselect("Age Group", options=age_groups, default=age_groups, key='age_group_filter')

        campaign_names = list(df_cleaned['campaign_name'].dropna().unique()) if 'campaign_name' in df_cleaned.columns else []
        campaign_name_filter = st.sidebar.multiselect("Campaign Name", options=campaign_names, default=campaign_names, key='campaign_name_filter')

        # Date Range Filter
        if 'date' in df_cleaned.columns and len(df_cleaned) > 0:
            min_date = df_cleaned['date'].min()
            max_date = df_cleaned['date'].max()
            start_date = st.sidebar.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date, key='start_date_filter')
            end_date = st.sidebar.date_input("End Date", value=max_date, min_value=start_date, max_value=max_date, key='end_date_filter')
        else:
            start_date = None
            end_date = None

        # Apply filtering
        df_filtered = filter_data(
            df=df_cleaned,
            campaign_objective=campaign_objective_filter,
            devices=device_filter,
            genders=gender_filter,
            age_groups=age_group_filter,
            campaign_names=campaign_name_filter,
            start_date=start_date,
            end_date=end_date
        )

        if df_filtered.empty:
            st.warning("No data matches current filters. Please adjust selection settings.")
            st.stop()

        # Run Analytics Engine
        basic_kpis = calculate_basic_kpis(df_filtered)
        perf_comparisons = compare_performance(df_filtered)
        segmented_analysis = analyze_segments(df_filtered)
        graph_data = prepare_graph_data(df_filtered)

        # Generate display-ready insights & recommendations
        kpi_summary = generate_kpi_summary(basic_kpis)
        best_perf_details = generate_best_performers(df_filtered, perf_comparisons)
        under_perf, high_perf, low_ctr_perf = generate_performer_insights(df_filtered, perf_comparisons)
        anomaly_insights = generate_anomaly_insights(df_filtered, anomalies)
        recommendations = generate_recommendations(df_filtered, perf_comparisons, segmented_analysis)
        
        # Build AI Summary
        ai_summary = build_ai_summary(
            kpis=kpi_summary,
            best_performance=best_perf_details,
            anomalies=anomalies,
            df=df_filtered,
            recommendations=recommendations,
            segmented_analysis=segmented_analysis
        )

        # AI Assistant Container
        with st.container(border=True):
            st.header("💡 Ask AI Assistant")
            prompt = st.text_area("Ask questions about your campaign data:", height=100)
            if st.button("Generate AI Insights"):
                if prompt.strip():
                    with st.spinner("AI is analyzing campaigns..."):
                        try:
                            ai_response = generate_ai_response(prompt, ai_summary)
                            st.subheader("AI Analysis Result:")
                            st.write(ai_response)
                        except Exception as e:
                            st.error(f"AI generation failed: {e}")
                else:
                    st.warning("Please enter a question.")

        # KPIs Section
        with st.container(border=True):
            st.header("📈 Key Performance Indicators (KPIs)")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="Total Spend", value=f"₹{kpi_summary['Total Spend']:,.2f}")
            with col2:
                st.metric(label="Total Impressions", value=f"{int(kpi_summary['Total Impressions']):,}")
            with col3:
                st.metric(label="Total Clicks", value=f"{int(kpi_summary['Total Clicks']):,}")
            
            col4, col5, col6 = st.columns(3)
            with col4:
                st.metric(label="Total Conversions", value=f"{int(kpi_summary['Total Conversions']):,}")
            with col5:
                st.metric(label="Total Reach", value=f"{int(kpi_summary['Total Reach']):,}")
            with col6:
                st.metric(label="Average CTR", value=f"{kpi_summary['Average CTR']}%")
            
            col7, col8, col9 = st.columns(3)
            with col7:
                st.metric(label="Average CPC", value=f"₹{kpi_summary['Average CPC']:.2f}")
            with col8:
                st.metric(label="Average CPM", value=f"₹{kpi_summary['Average CPM']:.2f}")
            with col9:
                st.metric(label="Conversion Rate", value=f"{kpi_summary['Conversion Effectiveness']}%")

        st.divider()

        # Best Performers
        with st.container(border=True):
            st.title("🏆 Best Performers")
            for basis, info in best_perf_details.items():
                st.subheader(f"Best Campaign by {basis.replace('_', ' ').title()}")
                st.write(f"**Campaign Name:** {info['Name']}")
                col_c1, col_c2, col_c3 = st.columns(3)
                with col_c1:
                    st.metric(label="Conversions", value=f"{int(info['Conversions'])}")
                with col_c2:
                    st.metric(label="CTR (%)", value=f"{info['CTR'] * 100:.4f}%")
                with col_c3:
                    st.metric(label="Spend", value=f"₹{info['Spend']:,.2f}")

                with st.expander("View Full Campaign Metrics"):
                    col_det1, col_det2, col_det3 = st.columns(3)
                    with col_det1:
                        st.metric(label="Clicks", value=f"{int(info['Clicks'])}")
                        st.metric(label="Purchases", value=f"{int(info['Purchases'])}")
                    with col_det2:
                        st.metric(label="Date", value=str(info['Date']))
                        st.metric(label="Impressions", value=f"{int(info['Impressions'])}")
                    with col_det3:
                        st.metric(label="CTA", value=str(info['CTA']))
                        st.metric(label="Budget", value=f"₹{info['Budget']:,.2f}")

        st.divider()

        # Performers Lists
        st.title("📊 Campaign Cohort Rankings")
        
        with st.expander("View High Performing Campaigns (Below Avg Spend & Above Avg CVR)"):
            if high_perf:
                st.dataframe(pd.DataFrame(high_perf).T)
            else:
                st.write("No campaigns match high performance criteria.")

        with st.expander("View Underperforming Campaigns (Above Avg Spend & Below Avg CVR)"):
            if under_perf:
                st.dataframe(pd.DataFrame(under_perf).T)
            else:
                st.write("No campaigns match underperformance criteria.")

        with st.expander("View Low CTR Campaigns (Below Average CTR)"):
            if low_ctr_perf:
                st.dataframe(pd.DataFrame(low_ctr_perf).T)
            else:
                st.write("No campaigns match low CTR criteria.")

        st.divider()

        # Segmented Analysis
        st.title("🧩 Cohort Segmentation Analysis")
        
        with st.expander("View Age Segment Analysis"):
            if not segmented_analysis['age_segment'].empty:
                st.dataframe(segmented_analysis['age_segment'].sort_values(by='Segment CTR', ascending=False))
        
        with st.expander("View Gender Segment Analysis"):
            if not segmented_analysis['gender_segment'].empty:
                st.dataframe(segmented_analysis['gender_segment'].sort_values(by='Segment CTR', ascending=False))

        with st.expander("View Device Segment Analysis"):
            if not segmented_analysis['device_segment'].empty:
                st.dataframe(segmented_analysis['device_segment'].sort_values(by='Segment CTR', ascending=False))

        with st.expander("View Objective Segment Analysis"):
            if not segmented_analysis['objective_segment'].empty:
                st.dataframe(segmented_analysis['objective_segment'].sort_values(by='Segment CTR', ascending=False))

        st.divider()

        # Anomalies
        with st.container(border=True):
            st.title("🚨 Business Rule Anomalies")
            anom_found = False
            for anom_type, details in anomaly_insights.items():
                if details:
                    anom_found = True
                    with st.expander(anom_type):
                        st.dataframe(pd.DataFrame(details).T)
            if not anom_found:
                st.success("No business rule anomalies detected in this dataset.")

        st.divider()

        # Recommendations
        st.title("💡 Actionable Recommendations")
        
        with st.container(border=True):
            st.header("Budget Reallocation")
            st.write("Consider increasing budget allocation to these high-performing campaigns:")
            if recommendations['Budget Reallocation']:
                st.dataframe(pd.DataFrame(recommendations['Budget Reallocation']).T)
            else:
                st.write("Insufficient data for budget reallocation recommendations.")

        with st.container(border=True):
            st.header("Spend Optimization")
            st.write("Consider reducing budgets or refining targeting for these underperforming high-spend campaigns:")
            if recommendations['Reduce Spend']:
                st.dataframe(pd.DataFrame(recommendations['Reduce Spend']).T)
            else:
                st.write("Insufficient data for spend reduction recommendations.")

        with st.container(border=True):
            st.header("Creative Optimization")
            st.write("These campaigns have below-average CTRs. Consider testing new copy, creatives, or formats:")
            if recommendations['Creative Optimization']:
                st.dataframe(pd.DataFrame(recommendations['Creative Optimization']).T)
            else:
                st.write("Insufficient data for creative optimization recommendations.")

        with st.container(border=True):
            st.header("Landing Page Optimization")
            st.write("These campaigns have high CTRs but low conversion rates, indicating a drop-off on landing pages:")
            if recommendations['Landing Page Optimization']:
                st.dataframe(pd.DataFrame(recommendations['Landing Page Optimization']).T)
            else:
                st.write("Insufficient data for landing page optimization recommendations.")

        with st.container(border=True):
            st.header("Targeting Recommendations")
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                st.subheader("Gender cohort")
                st.dataframe(recommendations['Gender'])
                st.subheader("Age group cohort")
                st.dataframe(recommendations['Age'])
            with col_t2:
                st.subheader("Device cohort")
                st.dataframe(recommendations['Device'])
                st.subheader("Campaign Objective cohort")
                st.dataframe(recommendations['Campaign'])

        st.divider()

        # Visualizations
        st.title("📉 Performance Visualizations")

        if 'campaign_name_vs_spend' in graph_data:
            st.plotly_chart(
                create_bar_chart(
                    graph_data['campaign_name_vs_spend'],
                    x_label="Campaign Name",
                    y_label="Total Spend (INR)",
                    title="Campaign Name vs Spend"
                ),
                use_container_width=True
            )

        if 'campaign_name_vs_conversion_rate' in graph_data:
            st.plotly_chart(
                create_bar_chart(
                    graph_data['campaign_name_vs_conversion_rate'],
                    x_label="Campaign Name",
                    y_label="Conversion Rate (%)",
                    title="Campaign Name vs Conversion Rate"
                ),
                use_container_width=True
            )

        if 'device_vs_conversion_rate' in graph_data:
            st.plotly_chart(
                create_bar_chart(
                    graph_data['device_vs_conversion_rate'],
                    x_label="Device",
                    y_label="Conversion Rate (%)",
                    title="Device vs Conversion Rate"
                ),
                use_container_width=True
            )

        if 'spend_vs_conversions' in graph_data:
            st.plotly_chart(
                create_scatter_chart(
                    graph_data['spend_vs_conversions'],
                    x_column="spend_inr",
                    y_column="conversions",
                    title="Spend vs Conversions Scatter Analysis",
                    x_label="Spend (INR)",
                    y_label="Conversions",
                    size_column="conversions",
                    color_column="conversions"
                ),
                use_container_width=True
            )

        # Advanced Visualizations
        with st.expander("Advanced Analytics Visualizations"):
            if 'campaign_name_vs_ctr' in graph_data:
                st.plotly_chart(
                    create_bar_chart(
                        graph_data['campaign_name_vs_ctr'],
                        x_label="Campaign Name",
                        y_label="CTR (%)",
                        title="Campaign Name vs CTR"
                    ),
                    use_container_width=True
                )

            if 'gender_vs_ctr' in graph_data:
                st.plotly_chart(
                    create_bar_chart(
                        graph_data['gender_vs_ctr'],
                        x_label="Gender",
                        y_label="CTR (%)",
                        title="Gender vs CTR"
                    ),
                    use_container_width=True
                )

            if 'gender_vs_conversion_rate' in graph_data:
                st.plotly_chart(
                    create_bar_chart(
                        graph_data['gender_vs_conversion_rate'],
                        x_label="Gender",
                        y_label="Conversion Rate (%)",
                        title="Gender vs Conversion Rate"
                    ),
                    use_container_width=True
                )

            if 'age_group_vs_ctr' in graph_data:
                st.plotly_chart(
                    create_bar_chart(
                        graph_data['age_group_vs_ctr'],
                        x_label="Age Group",
                        y_label="CTR (%)",
                        title="Age Group vs CTR"
                    ),
                    use_container_width=True
                )

            if 'age_group_vs_conversion_rate' in graph_data:
                st.plotly_chart(
                    create_bar_chart(
                        graph_data['age_group_vs_conversion_rate'],
                        x_label="Age Group",
                        y_label="Conversion Rate (%)",
                        title="Age Group vs Conversion Rate"
                    ),
                    use_container_width=True
                )

            if 'spend_over_time' in graph_data:
                st.plotly_chart(
                    create_line_chart(
                        graph_data['spend_over_time'],
                        x_label="Date",
                        y_label="Total Spend (INR)",
                        title="Spend Over Time"
                    ),
                    use_container_width=True
                )

            if 'clicks_over_time' in graph_data:
                st.plotly_chart(
                    create_line_chart(
                        graph_data['clicks_over_time'],
                        x_label="Date",
                        y_label="Total Clicks",
                        title="Clicks Over Time"
                    ),
                    use_container_width=True
                )

            if 'conversions_over_time' in graph_data:
                st.plotly_chart(
                    create_line_chart(
                        graph_data['conversions_over_time'],
                        x_label="Date",
                        y_label="Total Conversions",
                        title="Conversions Over Time"
                    ),
                    use_container_width=True
                )

            if 'ctr_over_time' in graph_data:
                st.plotly_chart(
                    create_line_chart(
                        graph_data['ctr_over_time'],
                        x_label="Date",
                        y_label="CTR (%)",
                        title="CTR Over Time"
                    ),
                    use_container_width=True
                )

            if 'spend_distribution_by_objective' in graph_data:
                st.plotly_chart(
                    create_pie_chart(
                        graph_data['spend_distribution_by_objective'],
                        title="Spend Distribution by Objective",
                        name_label="Objective"
                    ),
                    use_container_width=True
                )

            if 'conversions_distribution_by_objective' in graph_data:
                st.plotly_chart(
                    create_pie_chart(
                        graph_data['conversions_distribution_by_objective'],
                        title="Conversions Distribution by Objective",
                        name_label="Objective"
                    ),
                    use_container_width=True
                )

            if 'spend_vs_ctr' in graph_data:
                st.plotly_chart(
                    create_scatter_chart(
                        graph_data['spend_vs_ctr'],
                        x_column="spend_inr",
                        y_column="ctr_pct",
                        title="Spend vs CTR Scatter Analysis",
                        x_label="Spend (INR)",
                        y_label="CTR (%)",
                        size_column="spend_inr",
                        color_column="ctr_pct"
                    ),
                    use_container_width=True
                )

            if 'clicks_vs_conversions' in graph_data:
                st.plotly_chart(
                    create_scatter_chart(
                        graph_data['clicks_vs_conversions'],
                        x_column="clicks",
                        y_column="conversions",
                        title="Clicks vs Conversions Scatter Analysis",
                        x_label="Total Clicks",
                        y_label="Total Conversions",
                        size_column="conversions",
                        color_column="conversions"
                    ),
                    use_container_width=True
                )

            if 'impressions_vs_clicks' in graph_data:
                st.plotly_chart(
                    create_scatter_chart(
                        graph_data['impressions_vs_clicks'],
                        x_column="impressions",
                        y_column="clicks",
                        title="Impressions vs Clicks Scatter Analysis",
                        x_label="Total Impressions",
                        y_label="Total Clicks",
                        size_column="clicks",
                        color_column="clicks"
                    ),
                    use_container_width=True
                )
else:
    st.header("Please Upload a File to Get Started")
