"""Instagram Campaign Analyzer Orchestrator (Streamlit Application)
"""

import streamlit as st
import pandas as pd
import logging

from config.settings import MAPPING_DROPDOWN_OPTIONS
from Data.loader import file_load 
from Data.filter import filter_data
from mapping.column_mapper import map_columns
from cleaning.data_cleaner import clean_data
from validation.duplicate_validator import validate_no_duplicate_mappings
from validation.validator import run_validation
from analytics.analytics_engine import run_analytics_pipeline
from analytics.graph_data import prepare_graph_data
from analytics.anomaly_detection import detect_anomalies as detect_anomalies_new
from insights.insight_engine import (
    generate_kpi_summary,
    generate_best_performers,
    generate_performer_insights,
    generate_anomaly_insights,
)
from insights.recommendation_engine import generate_recommendations
from insights.summary_builder import build_ai_summary
from ai.ai_engine import generate_ai_response
from visualization.charts import (
    create_bar_chart,
    create_scatter_chart,
    create_line_chart,
    create_pie_chart,
)

from visualization.ui_components import (
    load_custom_css,
    render_header_banner,
    open_metric_primary,
    close_metric_primary,
    open_metric_secondary,
    close_metric_secondary,
    render_vertical_spacer
)

# Page configuration setup
st.set_page_config(
    page_title="Instagram Campaign Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject executive custom CSS stylesheet loaded from .streamlit/style.css
load_custom_css()
# Setup logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Render Header Banner using .streamlit template component
render_header_banner()

# File Upload Section
uploaded_file = st.file_uploader("Upload a CSV or PDF file containing campaign data to begin:", type=["csv", "pdf"])

if uploaded_file:
    if not uploaded_file.name.endswith(".csv") and not uploaded_file.name.endswith(".pdf"):
        st.error("Invalid Filetype. Please upload a CSV or PDF file.")
        st.stop()

    # Load raw data
    try:
        df_raw = file_load(uploaded_file, uploaded_file.name.lower())
    except Exception as e:
        logger.exception("Failed to load uploaded file")
        st.error(f"Invalid file format or corrupted file: {e}")
        st.stop()

    # Session State Initialization for mappings
    if "mapping_confirmed" not in st.session_state:
        st.session_state.mapping_confirmed = False

    if not st.session_state.mapping_confirmed:
        predicted_mapping = map_columns(df_raw)
        st.subheader("📋 Verify Column Mappings")
        st.write("Ensure your CSV headers map to the correct canonical metrics used by the analyzer.")
        
        user_mapping = {}
        with st.container(border=True):
            col_left, col_right = st.columns(2)
            with col_left:
                st.markdown("**Your CSV Column**")
            with col_right:
                st.markdown("**Canonical Field**")

            for column, predicted_alias in predicted_mapping.items():
                c_left, c_right = st.columns(2)
                with c_left:
                    st.text(column)
                with c_right:
                    default_idx = (
                        MAPPING_DROPDOWN_OPTIONS.index(predicted_alias)
                        if predicted_alias in MAPPING_DROPDOWN_OPTIONS
                        else 0
                    )
                    user_mapping[column] = st.selectbox(
                        f"Select mapping for {column}",
                        options=MAPPING_DROPDOWN_OPTIONS,
                        key=f"column_mapper_{column}",
                        index=default_idx,
                        label_visibility="collapsed"
                    )

        if st.button("Confirm Mappings and Initialize Dashboard", type="primary"):
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
        st.success("Mapping confirmed successfully!")
        if st.button("Open Analysis Suite", type="primary"):
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
            st.error("Uploaded dataset failed critical structural validation checks.")
            with st.expander("Show Validation Report Details", expanded=True):
                st.write(validation_report)
            st.stop()

        # Display non-blocking warnings in sidebar/top-bar
        with st.sidebar:
            st.header("⚡ Validation Logs")
            if validation_report['duplicates']['duplicate_row_count'] > 0:
                st.warning(f"⚠️ {validation_report['duplicates']['duplicate_row_count']} Duplicate Rows found.")
            if len(validation_report['missing']['rows_excessive_missing_idx']) > 0:
                st.warning(f"⚠️ {len(validation_report['missing']['rows_excessive_missing_idx'])} columns >50% empty.")
            if not validation_report['duplicates']['duplicate_row_count'] and not len(validation_report['missing']['rows_excessive_missing_idx']):
                st.success("✅ Structural integrity validated.")

        # Derived metrics discrepancies workflow
        metric_choice = "Calculated Metrics (Recommended)"
        if validation_report['derived_metrics']['has_discrepancies']:
            st.warning("⚠️ Discrepancies found between uploaded derived metrics and system-calculated values.")
            with st.expander("Inspect Derived Metric Differences"):
                discrepancies=validation_report['derived_metrics']['discrepancies']
                for discrepancy in discrepancies:
                    if discrepancies[discrepancy]:
                     st.subheader(discrepancy.upper())
                     st.dataframe(pd.DataFrame(discrepancies[discrepancy]), use_container_width=True)
            metric_choice = st.radio(
                "Source derived metrics to use for analysis:",
                options=["Calculated Metrics (Recommended)", "Uploaded Metrics"],
                key="derived_metric_choice"
            )

        # Apply derived metrics selection to mapping frame
        if metric_choice == "Calculated Metrics (Recommended)":
            df_mapped['ctr_pct'] = (df_mapped['clicks'] / df_mapped['impressions']).fillna(0.0) if 'impressions' in df_mapped.columns and 'clicks' in df_mapped.columns else 0.0
            df_mapped['cpc_inr'] = (df_mapped['spend_inr'] / df_mapped['clicks']).fillna(0.0) if 'spend_inr' in df_mapped.columns and 'clicks' in df_mapped.columns else 0.0
            df_mapped['conversion_rate_pct'] = (df_mapped['conversions'] / df_mapped['clicks']).fillna(0.0) if 'conversions' in df_mapped.columns and 'clicks' in df_mapped.columns else 0.0
        else:
            # Ensure uploaded metrics are normalized (0-1) for percentages to keep systems consistent
            for pct_col in ['ctr_pct', 'conversion_rate_pct']:
                if pct_col in df_mapped.columns:
                    max_val = df_mapped[pct_col].max()
                    if max_val > 1.0:
                        df_mapped[pct_col] = df_mapped[pct_col] / 100.0

        # Clean Data
        df_cleaned = clean_data(df_mapped)
        
        # Run anomaly detection module
        anom_res = detect_anomalies_new(df_cleaned)
        anomalies = anom_res['index_map']

        # Filters Sidebar setup
        st.sidebar.header("🎯 Filters")
        st.sidebar.write("Refine campaign data:")
        
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

        # Run Restructured Analytics Engine
        analytics_report = run_analytics_pipeline(df_filtered)
        
        # Prepare graph data
        graph_data = prepare_graph_data(df_filtered)

        # Map variables for UI compatibility
        basic_kpis = analytics_report['kpis']
        campaign_report = analytics_report['campaigns']
        audience_report = analytics_report['audience']
        device_report = analytics_report['devices']
        objective_report = analytics_report['objectives']
        
        # Helper functions to convert campaign names to dataframe indexes for UI compat
        def get_campaign_index(name):
            if not name or df_filtered.empty:
                return None
            matches = df_filtered[df_filtered['campaign_name'] == name]
            return matches.index[0] if not matches.empty else None

        def get_campaign_indexes(names):
            if not names or df_filtered.empty:
                return pd.Index([])
            return df_filtered[df_filtered['campaign_name'].isin(names)].index

        # Reconstruct performance comparison structure directly from campaign_report
        top_c = campaign_report['top_campaigns']
        bot_c = campaign_report['bottom_campaigns']
        campaign_metrics = campaign_report['campaign_metrics']
        
        high_perf_names = campaign_report.get('high_performers', [])
        low_perf_names = campaign_report.get('low_performers', [])
        
        # Low CTR and low landing page conversion names
        account_avg_ctr = basic_kpis.get('ctr', 0.0)
        account_avg_cvr = basic_kpis.get('conversion_rate', 0.0)
        
        low_ctr_names = [name for name, m in campaign_metrics.items() if m.get('ctr', 0.0) <= account_avg_ctr]
        low_lp_names = [name for name, m in campaign_metrics.items() if m.get('conversion_rate', 0.0) <= account_avg_cvr]

        perf_comparisons = {
            'Best CTR': get_campaign_index(top_c['highest_ctr']['name']),
            'Worst CTR': get_campaign_index(bot_c['lowest_ctr']['name']),
            'Highest conversion campaign': get_campaign_index(top_c['highest_conversion_rate']['name']),
            'Most expensive CPC': get_campaign_index(max(campaign_metrics.keys(), key=lambda k: campaign_metrics[k].get('cpc', 0.0))) if campaign_metrics else None,
            'highest spend': get_campaign_index(top_c['highest_spend']['name']),
            'Low performing campaigns': get_campaign_indexes(low_perf_names),
            'High performing campaigns': get_campaign_indexes(high_perf_names),
            'Low CTR campaigns': get_campaign_indexes(low_ctr_names),
            'Low Landing page conversion campaign': get_campaign_indexes(low_lp_names),
        }

        # Format segment analysis structures
        def dict_to_segment_df(data_dict):
            if not data_dict:
                return pd.DataFrame()
            df_seg = pd.DataFrame(data_dict).T
            rename_map = {
                'spend_inr': 'Total Spend',
                'impressions': 'Total Impressions',
                'clicks': 'Total Clicks',
                'conversions': 'Total Conversions',
                'ctr': 'Segment CTR',
                'cpc': 'Segment CPC',
                'conversion_rate': 'Segment Conversion Rate'
            }
            df_seg.rename(columns=rename_map, inplace=True)
            return df_seg

        segmented_analysis = {
            'age_segment': dict_to_segment_df(audience_report['age_analysis']),
            'gender_segment': dict_to_segment_df(audience_report['gender_analysis']),
            'device_segment': dict_to_segment_df(device_report['device_metrics']),
            'objective_segment': dict_to_segment_df(objective_report['objective_metrics'])
        }

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

        # Layout Main Dashboard using Tabs
        tab_overview, tab_cohorts, tab_recommendations, tab_ai, tab_audit = st.tabs([
            "📊 Overview Dashboard",
            "🧩 Cohorts & Segments",
            "💡 Actionable Advice",
            "🤖 AI Consultant",
            "🚨 Diagnostics & Audit"
        ])

        # --- TAB 1: OVERVIEW DASHBOARD ---
        with tab_overview:
            st.markdown("### 📊 Executive Summary & Core KPIs")
            
            # Primary Highlight KPIs
            open_metric_primary()
            kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
            with kpi_col1:
                st.metric(label="Total Ad Spend", value=f"₹{kpi_summary['Total Spend']:,.2f}")
            with kpi_col2:
                st.metric(label="Total Conversions", value=f"{int(kpi_summary['Total Conversions']):,}")
            with kpi_col3:
                st.metric(label="Average CTR", value=f"{kpi_summary['Average CTR']}%")
            with kpi_col4:
                st.metric(label="Conversion Rate", value=f"{kpi_summary['Conversion Effectiveness']}%")
            close_metric_primary()

            render_vertical_spacer()

            # Secondary Operational KPIs
            open_metric_secondary()
            kpi_col5, kpi_col6, kpi_col7, kpi_col8, kpi_col9 = st.columns(5)
            with kpi_col5:
                st.metric(label="Total Impressions", value=f"{int(kpi_summary['Total Impressions']):,}")
            with kpi_col6:
                st.metric(label="Total Clicks", value=f"{int(kpi_summary['Total Clicks']):,}")
            with kpi_col7:
                st.metric(label="Total Reach", value=f"{int(kpi_summary['Total Reach']):,}")
            with kpi_col8:
                st.metric(label="Average CPC", value=f"₹{kpi_summary['Average CPC']:.2f}")
            with kpi_col9:
                st.metric(label="Average CPM", value=f"₹{kpi_summary['Average CPM']:.2f}")
            close_metric_secondary()

            st.divider()

            # Best Performers Highlight Cards
            st.subheader("🏆 Best Performing Campaigns")
            best_cols = st.columns(len(best_perf_details))
            for i, (basis, info) in enumerate(best_perf_details.items()):
                with best_cols[i]:
                    with st.container(border=True):
                        st.markdown(f"### Best Campaign by **{basis.replace('_', ' ').title()}**")
                        st.markdown(f"**Name**: `{info['Name']}`")
                        st.write(f"📅 Date: {info['Date']}")
                        st.write(f"🎯 CTA: {info['CTA']}")
                        col_stat1, col_stat2 = st.columns(2)
                        with col_stat1:
                            st.metric("Conversions", f"{int(info['Conversions'])}")
                            st.metric("Spend", f"₹{info['Spend']:,.2f}")
                        with col_stat2:
                            st.metric("CTR (%)", f"{info['CTR'] * 100:.2f}%")
                            st.metric("Clicks", f"{int(info['Clicks'])}")

            st.divider()

            # Visualizations Layout (Side by Side)
            st.subheader("📉 Campaign Performance Visualizations")
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
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
            with col_chart2:
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

            col_chart3, col_chart4 = st.columns(2)
            with col_chart3:
                if 'spend_vs_conversions' in graph_data:
                    st.plotly_chart(
                        create_scatter_chart(
                            graph_data['spend_vs_conversions'],
                            x_column="spend_inr",
                            y_column="conversions",
                            title="Spend vs Conversions (Cost Efficiency)",
                            x_label="Spend (INR)",
                            y_label="Conversions",
                            size_column="conversions",
                            color_column="conversions"
                        ),
                        use_container_width=True
                    )
            with col_chart4:
                if 'spend_over_time' in graph_data:
                    st.plotly_chart(
                        create_line_chart(
                            graph_data['spend_over_time'],
                            x_label="Date",
                            y_label="Total Spend (INR)",
                            title="Spend Over Time (Timeline)"
                        ),
                        use_container_width=True
                    )

        # --- TAB 2: COHORTS & SEGMENTS ---
        with tab_cohorts:
            st.subheader("🧩 Audience Cohorts breakdown")
            
            col_seg1, col_seg2 = st.columns(2)
            with col_seg1:
                st.markdown("#### Age Group Cohorts")
                if not segmented_analysis['age_segment'].empty:
                    st.dataframe(segmented_analysis['age_segment'].sort_values(by='Segment CTR', ascending=False), use_container_width=True)
            with col_seg2:
                st.markdown("#### Gender Cohorts")
                if not segmented_analysis['gender_segment'].empty:
                    st.dataframe(segmented_analysis['gender_segment'].sort_values(by='Segment CTR', ascending=False), use_container_width=True)

            col_seg3, col_seg4 = st.columns(2)
            with col_seg3:
                st.markdown("#### Device Type Cohorts")
                if not segmented_analysis['device_segment'].empty:
                    st.dataframe(segmented_analysis['device_segment'].sort_values(by='Segment CTR', ascending=False), use_container_width=True)
            with col_seg4:
                st.markdown("#### Marketing Objective Cohorts")
                if not segmented_analysis['objective_segment'].empty:
                    st.dataframe(segmented_analysis['objective_segment'].sort_values(by='Segment CTR', ascending=False), use_container_width=True)

            st.divider()
            st.subheader("📊 Cohort Performance Graphs")
            
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                if 'device_vs_conversion_rate' in graph_data:
                    st.plotly_chart(
                        create_bar_chart(
                            graph_data['device_vs_conversion_rate'],
                            x_label="Device",
                            y_label="Conversion Rate (%)",
                            title="Conversion Rate by Device Type"
                        ),
                        use_container_width=True
                    )
            with col_g2:
                if 'gender_vs_ctr' in graph_data:
                    st.plotly_chart(
                        create_bar_chart(
                            graph_data['gender_vs_ctr'],
                            x_label="Gender",
                            y_label="CTR (%)",
                            title="CTR by Gender Cohort"
                        ),
                        use_container_width=True
                    )

            col_g3, col_g4 = st.columns(2)
            with col_g3:
                if 'age_group_vs_ctr' in graph_data:
                    st.plotly_chart(
                        create_bar_chart(
                            graph_data['age_group_vs_ctr'],
                            x_label="Age Group",
                            y_label="CTR (%)",
                            title="CTR by Age Group Cohort"
                        ),
                        use_container_width=True
                    )
            with col_g4:
                if 'spend_distribution_by_objective' in graph_data:
                    st.plotly_chart(
                        create_pie_chart(
                            graph_data['spend_distribution_by_objective'],
                            title="Spend Distribution by Campaign Objective",
                            name_label="Objective"
                        ),
                        use_container_width=True
                    )

        # --- TAB 3: ACTIONABLE ADVICE ---
        with tab_recommendations:
            st.subheader("💡 Strategic Recommendations & Interventions")

            col_rec1, col_rec2 = st.columns(2)
            with col_rec1:
                with st.container(border=True):
                    st.markdown("### 💰 Budget Reallocation")
                    st.write("Increase budget allocations for these highly effective, cost-efficient campaigns:")
                    if recommendations['Budget Reallocation']:
                        st.dataframe(pd.DataFrame(recommendations['Budget Reallocation']).T, use_container_width=True)
                    else:
                        st.write("No campaigns identified for budget reallocation currently.")

            with col_rec2:
                with st.container(border=True):
                    st.markdown("### ⚠️ Spend Optimization")
                    st.write("Reduce budgets or refine targeting on these high-spend, low-conversion campaigns:")
                    if recommendations['Reduce Spend']:
                        st.dataframe(pd.DataFrame(recommendations['Reduce Spend']).T, use_container_width=True)
                    else:
                        st.write("No campaigns identified for spend reduction currently.")

            col_rec3, col_rec4 = st.columns(2)
            with col_rec3:
                with st.container(border=True):
                    st.markdown("### 🎨 Creative Optimization")
                    st.write("These campaigns have below-average CTRs. Refresh ad creatives or copy text:")
                    if recommendations['Creative Optimization']:
                        st.dataframe(pd.DataFrame(recommendations['Creative Optimization']).T, use_container_width=True)
                    else:
                        st.write("No campaigns require creative updates currently.")

            with col_rec4:
                with st.container(border=True):
                    st.markdown("### 🕸️ Landing Page Optimization")
                    st.write("High interest (CTR) but low conversions. Improve landing page experience:")
                    if recommendations['Landing Page Optimization']:
                        st.dataframe(pd.DataFrame(recommendations['Landing Page Optimization']).T, use_container_width=True)
                    else:
                        st.write("No landing page bottlenecks detected currently.")

            st.subheader("🎯 Top Performing Cohorts to Target")
            with st.container(border=True):
                col_tr1, col_tr2, col_tr3, col_tr4 = st.columns(4)
                with col_tr1:
                    st.markdown("#### Gender Cohort")
                    st.dataframe(recommendations['Gender'])
                with col_tr2:
                    st.markdown("#### Age Group")
                    st.dataframe(recommendations['Age'])
                with col_tr3:
                    st.markdown("#### Device Type")
                    st.dataframe(recommendations['Device'])
                with col_tr4:
                    st.markdown("#### Objective")
                    st.dataframe(recommendations['Campaign'])

        # --- TAB 4: AI CONSULTANT ---
        with tab_ai:
            st.subheader("🤖 Ask Your Campaign AI Consultant")
            st.write("Inquire about custom segments, correlations, or request copy suggestions based on your data:")
            
            prompt = st.text_area("Question/Prompt:", placeholder="Which target audience segment is performing best, and what should we optimize next?", height=120)
            if st.button("Consult AI Assistant", type="primary"):
                if prompt.strip():
                    with st.spinner("AI is evaluating campaign metrics..."):
                        try:
                            ai_response = generate_ai_response(prompt, ai_summary)
                            st.markdown("### 🤖 Consultant Response:")
                            st.write(ai_response)
                        except Exception as e:
                            st.error(f"AI generation failed: {e}")
                else:
                    st.warning("Please enter a question or query.")

        # --- TAB 5: DIAGNOSTICS & AUDIT ---
        with tab_audit:
            st.subheader("🚨 Business Logic & Data Discrepancy Audits")

            # Duplicate row reports
            st.markdown("#### Duplicates Inspection")
            if validation_report['duplicates']['duplicate_row_count'] > 0:
                st.warning(f"Found {validation_report['duplicates']['duplicate_row_count']} completely identical rows.")
                if 'duplicate_rows_data' in validation_report['duplicates']:
                    st.dataframe(validation_report['duplicates']['duplicate_rows_data'], use_container_width=True)
            else:
                st.success("No duplicate rows found.")

            # Missing value reports
            st.markdown("#### Missing Field Inspection")
            with st.expander("Inspect Missing Value Densities"):
                for missing in (validation_report['missing']):
                    if validation_report['missing'][missing] and type(validation_report['missing'][missing]) != bool:
                        st.dataframe(validation_report['missing'][missing])

            # Business anomalies
            st.markdown("#### Logical Anomalies Detected")
            anom_found = False
            for anom_type, details in anomaly_insights.items():
                if details:
                    anom_found = True
                    with st.expander(anom_type):
                        st.dataframe(pd.DataFrame(details).T, use_container_width=True)
            if not anom_found:
                st.success("No campaign-level logical anomalies detected in cleaned dataset.")
            st.markdown("#### Detailed Diagnostic Pipeline Logs")
            with st.expander("Open Validation Pipeline Outputs"):
             st.write(validation_report)

            st.divider()
            
            # Rankings
            st.subheader("📊 Full Cohort Rankings Data")
            with st.expander("High Performing Campaigns"):
                st.dataframe(pd.DataFrame(high_perf).T, use_container_width=True)
            with st.expander("Underperforming Campaigns"):
                st.dataframe(pd.DataFrame(under_perf).T, use_container_width=True)
            with st.expander("Low CTR Campaigns"):
                st.dataframe(pd.DataFrame(low_ctr_perf).T, use_container_width=True)
else:
    # App landing info when no file is uploaded
    st.info("👋 Upload a campaign CSV file in the selector widget to start the analysis pipeline.")
    
    with st.container(border=True):
        st.subheader("💡 Dashboard Features Include:")
        col_landing1, col_landing2, col_landing3 = st.columns(3)
        with col_landing1:
            st.markdown("#### 1. Mapping & Validation")
            st.write("Dynamic column mapping helps ingest any layout format, running structural audits for clean records.")
        with col_landing2:
            st.markdown("#### 2. Advanced Segmentations")
            st.write("Aggregates campaign performances by Age Group, Gender, Device, and Objectives automatically.")
        with col_landing3:
            st.markdown("#### 3. AI Insights")
            st.write("Leverages Google Gemini models to answer business questions instantly.")
