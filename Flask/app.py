from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import base64
import os
from google import genai
from google.genai import types
import json

API_KEY = "AIzaSyDPrLs7uipDUlLO2-7ygIUaevBOWnf21N0"

app = Flask(__name__)

def generate(text):
    client = genai.Client(
        api_key = API_KEY #os.environ.get("GEMINI_API_KEY"),
    )

    model = "gemini-2.5-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""Extract claims from this text and verify them. classify each claim in one of the following ways: True, False or Uncertain. Search internet for evidence supporting or opposing the claim. Return the response in JSON format. In json object return claim text, claim validity, sources used for verifying claim, confidence on verdict(range 1 to 100), category of claim (health, finance, sports, etc.). For each source provide source name, url, text from source used for verification, source credibility(range 0-100).  Also provide some reasoning to justify your verdict."""),
                types.Part.from_text(text=f"{text}"),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        thinking_config = types.ThinkingConfig(
            thinking_budget=0,
        ),
        response_mime_type="application/json",
        response_schema=genai.types.Schema(
            type = genai.types.Type.OBJECT,
            required = ["claims"],
            properties = {
                "claims": genai.types.Schema(
                    type = genai.types.Type.ARRAY,
                    items = genai.types.Schema(
                        type = genai.types.Type.OBJECT,
                        required = ["claim_text", "claim_validity", "sources_cited", "confidence", "reasoning"],
                        properties = {
                            "claim_text": genai.types.Schema(
                                type = genai.types.Type.STRING,
                            ),
                            "claim_validity": genai.types.Schema(
                                type = genai.types.Type.STRING,
                            ),
                            "sources_cited": genai.types.Schema(
                                type = genai.types.Type.ARRAY,
                                items = genai.types.Schema(
                                    type = genai.types.Type.OBJECT,
                                    required = ["source_name", "source_link", "source_credibility", "source_text"],
                                    properties = {
                                        "source_name": genai.types.Schema(
                                            type = genai.types.Type.STRING,
                                        ),
                                        "source_link": genai.types.Schema(
                                            type = genai.types.Type.STRING,
                                        ),
                                        "source_credibility": genai.types.Schema(
                                            type = genai.types.Type.INTEGER,
                                        ),
                                        "source_text": genai.types.Schema(
                                            type = genai.types.Type.STRING,
                                        ),
                                    },
                                ),
                            ),
                            "confidence": genai.types.Schema(
                                type = genai.types.Type.INTEGER,
                            ),
                            "reasoning": genai.types.Schema(
                                type = genai.types.Type.STRING,
                            ),
                        },
                    ),
                ),
            },
        ),
    )

    output = ''

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        print(chunk.text, end="")
        output += chunk.text
    
    return output

data = """{"claims": [{"claim_text": "Good sleep is important for work efficiency, endurance, disease prevention, and mental health.", "claim_validity": "True", "sources_cited": [{"source_name": "National Heart, Lung, and Blood Institute", "source_link": "https://www.nhlbi.nih.gov/health-topics/sleep-deprivation-and-deficiency", "source_credibility": 95, "source_text": "Sleep plays a vital role in good health and well-being throughout your life. Getting enough quality sleep at the right times can help protect your mental health, physical health, quality of life, and safety. The way you feel when you're awake depends in part on what happens while you're sleeping. During sleep, your body is hard at work supporting healthy brain function and maintaining your physical health."}], "confidence": 98, "reasoning": "Multiple reputable sources, including the National Heart, Lung, and Blood Institute, confirm that good sleep is crucial for various aspects of physical and mental health, including work efficiency and disease prevention."}, {"claim_text": "Poor sleep and sleep deprivation are associated with cardiovascular and metabolic diseases, impaired mental capacity, and poor motor coordination.", "claim_validity": "True", "sources_cited": [{"source_name": "Mayo Clinic", "source_link": "https://www.mayoclinic.org/diseases-conditions/sleep-deprivation/symptoms-causes/syc-20353079", "source_credibility": 90, "source_text": "Sleep deprivation can have serious consequences. Chronic sleep deprivation can put you at risk of developing several serious medical conditions, including high blood pressure, diabetes, heart attack, heart failure, and stroke. Other potential problems include obesity, depression, and a weakened immune system. Sleep deprivation also impairs your cognitive function, memory, and motor skills."}], "confidence": 97, "reasoning": "The Mayo Clinic corroborates that chronic sleep deprivation can lead to serious medical conditions like cardiovascular and metabolic diseases, and also impairs cognitive function and motor skills."}, {"claim_text": "A CO2 level of over 2,000 ppm can lead to headaches, poor concentration, increased heart rate, and nausea.", "claim_validity": "True", "sources_cited": [{"source_name": "Centers for Disease Control and Prevention (CDC) - NIOSH", "source_link": "https://www.cdc.gov/niosh/idlh/124389.html", "source_credibility": 95, "source_text": "NIOSH considers 40,000 ppm as immediately dangerous to life or health (IDLH). At 2,000 ppm, symptoms like headache, poor concentration, and increased heart rate can occur."}], "confidence": 95, "reasoning": "The National Institute for Occupational Safety and Health (NIOSH) confirms that CO2 levels above 2,000 ppm can cause symptoms such as headaches, poor concentration, and increased heart rate."}, {"claim_text": "A CO2 level above 40,000 ppm can cause brain damage, comas, and even death.", "claim_validity": "True", "sources_cited": [{"source_name": "Centers for Disease Control and Prevention (CDC) - NIOSH", "source_link": "https://www.cdc.gov/niosh/idlh/124389.html", "source_credibility": 95, "source_text": "NIOSH considers 40,000 ppm as immediately dangerous to life or health (IDLH), meaning exposure could lead to death, serious injury, or permanent health effects."}], "confidence": 95, "reasoning": "NIOSH explicitly states that 40,000 ppm is 'immediately dangerous to life or health (IDLH)', indicating the potential for severe outcomes including brain damage, coma, and death."}, {"claim_text": "You can achieve thermoneutrality (where the body doesn’t have to regulate its own temperature) without wearing pajamas at an environmental temperature of 86–90°F (30–32°C) or wearing pajamas and covering yourself with at least one sheet at 61–66°F (16–19°C).", "claim_validity": "Uncertain", "sources_cited": [{"source_name": "Sleep Foundation", "source_link": "https://www.sleepfoundation.org/bedroom-environment/temperature", "source_credibility": 80, "source_text": "Most sleep experts agree that the ideal bedroom temperature for sleep is between 60 and 67 degrees Fahrenheit (15.6 and 19.4 degrees Celsius). When you sleep, your body's internal temperature actually drops. A cooler room helps facilitate this natural temperature drop."}], "confidence": 60, "reasoning": "The Sleep Foundation suggests an ideal bedroom temperature range that is significantly lower than the 86-90°F (30-32°C) mentioned for sleeping without pajamas to achieve thermoneutrality. While the concept of thermoneutrality is valid, the specific temperature ranges provided in the claim, especially the higher one, are not directly supported by readily available expert consensus on ideal sleep temperatures. The lower range for sleeping with pajamas is closer to recommended temperatures, but the precise conditions for achieving thermoneutrality across varying clothing/bedding combinations are complex and less universally agreed upon with specific numbers."},{"claim_text": "Ideally, humidity in the bedroom should be between 40–60%.", "claim_validity": "True", "sources_cited": [{"source_name": "Environmental Protection Agency (EPA)", "source_link": "https://www.epa.gov/indoor-air-quality-iaq/indoor-air-quality-home", "source_credibility": 90, "source_text": "The EPA recommends maintaining indoor relative humidity between 30% and 50% to prevent mold growth and reduce the presence of other biological pollutants. Some sources suggest a range of 40-60% for comfort and health."}], "confidence": 90, "reasoning": "The Environmental Protection Agency (EPA) generally recommends 30-50% humidity to prevent mold, and many sources for comfort and health often cite 40-60% as ideal, making the claim largely consistent with expert advice."}, {"claim_text": "Air pollution affects sleep by acting upon the central nervous system and the upper airways, leading to reduced oxygen levels, respiratory acidosis, and obstructive sleep apnea.", "claim_validity": "True", "sources_cited": [{"source_name": "American Academy of Sleep Medicine (AASM)", "source_link": "https://jcsm.aasm.org/doi/10.5664/jcsm.6917", "source_credibility": 90, "source_text": "There is growing evidence that exposure to air pollution, particularly fine particulate matter (PM2.5), is associated with sleep disorders, including obstructive sleep apnea, and altered sleep architecture. Air pollutants can induce systemic inflammation and oxidative stress, affecting the central nervous system and respiratory pathways, which can lead to sleep disturbances."}], "confidence": 95, "reasoning": "The American Academy of Sleep Medicine indicates that air pollution is linked to sleep disorders like obstructive sleep apnea and can affect the central nervous system and respiratory pathways, aligning with the claim."}, {"claim_text": "Noises above 50dB will shorten your total sleeping time.", "claim_validity": "True", "sources_cited": [{"source_name": "World Health Organization (WHO)", "source_link": "https://www.who.int/publications/i/item/9789289002573", "source_credibility": 95, "source_text": "For a good night's sleep, the WHO recommends that the average night noise level should not exceed 40 dB. Prolonged exposure to noise levels above 50 dB can lead to sleep disturbance, including reduced sleep duration and poorer sleep quality."}], "confidence": 90, "reasoning": "The World Health Organization (WHO) explicitly states that prolonged exposure to noise levels above 50 dB can cause sleep disturbance, including reduced sleep duration."}, {"claim_text": "Low-frequency noises may also affect sleep quality by increasing the time it takes to fall asleep and causing you to feel tired in the morning.", "claim_validity": "True", "sources_cited": [{"source_name": "Environmental Health Perspectives (NIH)", "source_link": "https://ehp.niehs.nih.gov/doi/10.1289/ehp.119-a178", "source_credibility": 90, "source_text": "Studies have shown that low-frequency noise, often associated with road traffic and industrial sources, can penetrate buildings more easily and disrupt sleep, leading to increased sleep latency (time to fall asleep) and reduced sleep efficiency, resulting in feelings of tiredness upon waking."}], "confidence": 90, "reasoning": "Research published in Environmental Health Perspectives confirms that low-frequency noise can increase sleep latency and reduce sleep efficiency, contributing to morning tiredness."}, {"claim_text": "When the eye detects the slightest source of light during the night, the production of melatonin is stopped and sleep is affected.", "claim_validity": "True", "sources_cited": [{"source_name": "Harvard Health Publishing", "source_link": "https://www.health.harvard.edu/staying-healthy/blue-light-has-a-dark-side", "source_credibility": 90, "source_text": "Light at night, especially blue light from electronic screens, suppresses the body's production of melatonin, a hormone that helps us fall asleep. Even dim light can interfere with a person's circadian rhythm and melatonin secretion."}], "confidence": 95, "reasoning": "Harvard Health Publishing confirms that even dim light at night can suppress melatonin production, thereby interfering with sleep and circadian rhythm."}, {"claim_text": "Sleeping with a night-light, staying up late in front of the TV or computer screen, and using your phone have all been shown to interfere with sleep.", "claim_validity": "True", "sources_cited": [{"source_name": "National Sleep Foundation", "source_link": "https://www.thensf.org/how-light-affects-your-sleep/", "source_credibility": 85, "source_text": "Exposure to light, especially blue light emitted from electronic devices like smartphones, computers, and TVs, before bed can disrupt the natural production of melatonin, making it harder to fall asleep and impacting sleep quality. Night-lights, even if dim, can also send signals to the brain that it's daytime, interfering with sleep."}], "confidence": 95, "reasoning": "The National Sleep Foundation and Harvard Health Publishing both confirm that light from electronic devices and even night-lights can interfere with sleep by suppressing melatonin production."}, {"claim_text": "There is strong controversy among specialists regarding the impact of electromagnetic fields (EMF) on the human body and sleep.", "claim_validity": "True", "sources_cited": [{"source_name": "World Health Organization (WHO)", "source_link": "https://www.who.int/news-room/questions-and-answers/item/electromagnetic-fields-and-public-health", "source_credibility": 95, "source_text": "A large amount of research has been carried out over the last two decades to assess whether mobile phones pose a potential health risk. To date, no adverse health effects have been established as being caused by mobile phone use. However, some individuals report symptoms, and ongoing research continues to explore this area."}], "confidence": 90, "reasoning": "The World Health Organization (WHO) acknowledges ongoing research and reported symptoms related to electromagnetic fields, indicating that while no definitive adverse health effects have been established, there is still an active area of investigation and public concern, leading to controversy among specialists."}, {"claim_text": "Exercising in the morning or throughout the day definitely increases both the quality and duration of sleep.", "claim_validity": "True", "sources_cited": [{"source_name": "Johns Hopkins Medicine", "source_link": "https://www.hopkinsmedicine.org/health/wellness-and-prevention/exercising-for-better-sleep", "source_credibility": 90, "source_text": "Regular exercise can improve sleep quality and duration. Moderate-intensity aerobic exercise can decrease the amount of time it takes to fall asleep (sleep latency) and increase the amount of time spent in deep, restorative sleep. It is generally recommended to avoid strenuous exercise too close to bedtime as it can be stimulating."}], "confidence": 95, "reasoning": "Johns Hopkins Medicine confirms that regular exercise improves sleep quality and duration, aligning with the claim, while also noting the caveat about exercising too close to bedtime."}, {"claim_text": "Rumination (repetitively going over the same thought or problem) has been proven to create a negative mood that will impair your sleep.", "claim_validity": "True", "sources_cited": [{"source_name": "American Psychological Association (APA)", "source_link": "https://www.apa.org/news/press/releases/2021/03/sleep-rumination-stress", "source_credibility": 95, "source_text": "Rumination is a common cognitive process characterized by repetitive and passive thinking about negative feelings and problems. It is consistently associated with worse sleep quality, including longer sleep onset latency and more awakenings, as it contributes to increased physiological and cognitive arousal."}], "confidence": 98, "reasoning": "The American Psychological Association (APA) clearly states that rumination is consistently associated with worse sleep quality due to increased arousal, directly supporting the claim."}, {"claim_text": "Establishing a bedtime routine and having consistent sleep-wake times improve sleep quality and reduce the amount of time it takes to fall asleep.", "claim_validity": "True", "sources_cited": [{"source_name": "National Sleep Foundation", "source_link": "https://www.thensf.org/how-to-create-a-healthy-sleep-routine/", "source_credibility": 85, "source_text": "A consistent sleep schedule and a relaxing bedtime routine are fundamental for good sleep hygiene. They help regulate your body's internal clock (circadian rhythm), making it easier to fall asleep and wake up at the same time each day, improving overall sleep quality and reducing sleep latency."}], "confidence": 98, "reasoning": "The National Sleep Foundation emphasizes that consistent sleep schedules and bedtime routines are fundamental for good sleep hygiene, regulating circadian rhythm and improving sleep quality and latency."}, {"claim_text": "Using smartphones in bed and being exposed to blue light has been associated with longer sleep latency, sleep disturbances, and decreased performance the next day.", "claim_validity": "True", "sources_cited": [{"source_name": "American Academy of Sleep Medicine (AASM)", "source_link": "https://jcsm.aasm.org/doi/10.5664/jcsm.4707", "source_credibility": 90, "source_text": "The use of light-emitting electronic devices (LE-EDs) before bedtime, particularly those emitting blue light, has been consistently linked to delayed sleep onset (longer sleep latency), reduced melatonin secretion, and poorer sleep quality, which can negatively impact daytime alertness and cognitive performance."}], "confidence": 97, "reasoning": "The American Academy of Sleep Medicine confirms that using light-emitting electronic devices before bed, especially those emitting blue light, is linked to delayed sleep onset, reduced melatonin, and poorer sleep quality, affecting next-day performance."}, {"claim_text": "Significant changes in sleep duration and deviations from the norm are usually associated with tobacco exposure, hypercholesterolemia, screen time, and body weight.", "claim_validity": "True", "sources_cited": [{"source_name": "Sleep Foundation", "source_link": "https://www.sleepfoundation.org/insomnia/sleep-deprivation-causes", "source_credibility": 80, "source_text": "Several lifestyle factors can impact sleep duration and quality. These include smoking (tobacco use), excessive screen time, and an unhealthy diet leading to obesity. Additionally, medical conditions such as high cholesterol (hypercholesterolemia) can also disrupt sleep patterns."}], "confidence": 90, "reasoning": "The Sleep Foundation corroborates that lifestyle factors like tobacco use, screen time, and body weight, along with medical conditions like hypercholesterolemia, are associated with altered sleep duration and patterns."}, {"claim_text": "Obese children typically experience shorter sleep duration and variable sleep patterns.", "claim_validity": "True", "sources_cited": [{"source_name": "American Academy of Pediatrics (AAP)", "source_link": "https://publications.aap.org/pediatrics/article/131/Supplement_1/S20/30620/Obesity-and-Sleep-in-Childhood-Sleep-Disorders", "source_credibility": 95, "source_text": "Numerous studies have shown a strong association between obesity and sleep in children, with obese children often exhibiting shorter sleep durations, poorer sleep quality, and more variable sleep patterns compared to their non-obese counterparts."}], "confidence": 95, "reasoning": "The American Academy of Pediatrics confirms a strong association between obesity in children and shorter, more variable sleep patterns."}, {"claim_text": "TV viewing and the presence of a TV in the bedroom is also associated with shorter sleep duration.", "claim_validity": "True", "sources_cited": [{"source_name": "National Sleep Foundation", "source_link": "https://www.thensf.org/electronic-devices-and-sleep/", "source_credibility": 85, "source_text": "Having a television in the bedroom or watching TV close to bedtime can negatively impact sleep duration and quality. The light emitted, particularly blue light, can suppress melatonin production, and the content can be stimulating, making it harder to fall asleep."}], "confidence": 90, "reasoning": "The National Sleep Foundation states that TV viewing, especially near bedtime or having a TV in the bedroom, can negatively impact sleep duration and quality due to light emission and stimulating content."}, {"claim_text": "The choice of pillows, mattresses, and a bed is highly subjective, with no one product that will suit everyone, and specialists recommend choosing according to personal taste and budget if no special orthopedic problems or other health issues are involved.", "claim_validity": "True", "sources_cited": [{"source_name": "Sleep Foundation", "source_link": "https://www.sleepfoundation.org/beds-and-accessories/best-mattress", "source_credibility": 80, "source_text": "There is no single 'best' mattress or pillow for everyone. The ideal choice depends on individual preferences, sleep position, body type, and any existing health conditions. Experts advise considering personal comfort, support needs, and budget when making these selections, especially if no specific medical issues require a particular type."}], "confidence": 95, "reasoning": "The Sleep Foundation confirms that the choice of sleep accessories is highly subjective and depends on individual factors, recommending personal preference and budget as key drivers in the absence of specific health needs."}]}"""


@app.route('/')
def home():
    return render_template("home.html")
    

@app.route('/test', methods=['POST'])
def test():
    url = request.form['url']
    text = scrape_article_text(url)
    data = generate(text)
    return json.loads(data)


# function that gets text from news articles
def scrape_article_text(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        text_elements = soup.find_all(['p', 'article']) # getting content from <p> tags
        
        full_text = []
        for element in text_elements:
            text = element.get_text(separator=" ", strip=True)
            if len(text) > 40:
                full_text.append(text)

        article_text = "\n".join(full_text)
        return article_text

    except Exception as e:
        print(f"Error: {e}")
        return ""
    
if __name__ == '__main__':
    app.run(debug=True)
    
