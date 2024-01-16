import os

from openai import OpenAI

client = OpenAI(
  organization= os.getenv('OPENAI_ORGANIZATION'),
)

def generate_image(music_name):
    description = client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[
        {"role": "system", "content": "Search the internet to get information of particular music, and extracts words to generate an image to express the music. Then, summarize pictorial explanation into one sentence. The explation should not be abstract. And convert the sentence to form that dall-e can understand. Only give me the Dall-e prompt."},
        { "role": "user", "content": music_name }
    ])
    
    return client.images.generate(
        model="dall-e-2",
        prompt=description.choices[0].message.content + ' The image should include at least one person.',
        n=1, 
        size="512x1024"
    )

def describe_image(music_name, images):
  # response = client.chat.completions.create(
  #   model="gpt-4-vision-preview",
  #   messages=[
  #     {
  #       "role": "user",
  #       "content": [
  #         {"type": "text", "text": "Describe the image associating the music '" + music_name + "'."},
  #         {
  #           "type": "image_url",
  #           "image_url": {
  #             "url": images[0],
  #           },
  #         },
  #       ],
  #     }
  #   ],
  #   max_tokens=300,
  # )
    
  response = client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[
        {"role": "system", "content": "Describe the music in one sentence. I need the musical feeling of '" + music_name + "'."},
    ])

  return response.choices[0].message.content