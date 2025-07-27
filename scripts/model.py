from transformers import pipeline

scrapped_text = r"C:\Users\Piyush\Documents\Bnp_Hack-15\News-scrapper\data\scraped.txt"
model_path = r"C:\Users\Piyush\Documents\Bnp_Hack-15\News-scrapper\models"

# Specify the device parameter (0 for the first GPU, -1 for CPU)
pipe = pipeline("text-classification", model=model_path, device=0)

# Perform inference
result = pipe(scrapped_text)
print(result)

# neutral, hard, sell, soft sell, buy