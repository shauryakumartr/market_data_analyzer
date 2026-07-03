import random
with open("/Users/shauryakumartr/Downloads/instagram_campaign_csv_analyzer_dataset_new_corrupt.csv",'rb') as a:
    data=bytearray(a.read())
file_size = int(len(data))
num_bytes_to_corrupt = int(file_size * float(0.05))
for _ in range(num_bytes_to_corrupt):
    random_index = random.randint(0, len(data) - 1)
    random_byte = random.randint(0, 255)
    data[random_index] = random_byte

with open("/Users/shauryakumartr/Downloads/instagram_campaign_csv_analyzer_dataset_new_final_corrupt.csv", "wb") as f:
    f.write(data)

