# Assignment #3
# Create a standalone program (command line application), which is uses large language model (LLM) to be a creative writer 
# e.g. marketing materials, memes, song lyrics, poems or blog posts, 
# which are search engine optimized (SEO) by using as many possible synonyms as possible. 
# The program should by default produce 3 different versions from the same prompt. 
# Try adjusting the system prompt, temperature, top-p, presence penalty and frequency penalty for best possible results. 
# Use OpenAI API. You are free to use any version of LLM you want, but try to choose a one suitable for the project 
# (e.g. gpt-4o-mini is most likely not ideal).


from openai import OpenAI

# LM Studio is running on localhost:1234
# Make sure to start LM Studio first

# Point to the local server
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

#  client.chat.completions.create
# a method that is used to create responses in conversational format.
# history = list, a list of dictionaries, 
# each dictionary contains a role and content.
# The role can be "system", "user", or "assistant".
# The content is the actual message.

history = [
    {"role": "system",
     "content": "You are a creative content writer specializing in travel. Write a short blog post based on the topic given below. Ensure the writing is search engine optimized (SEO) by using varied synonyms and phrases. Produce three distinct versions of the content. Start the piece with a captivating introduction and include at least three cities with short descriptions. End with a compelling call-to-action.Don't use a preamble.Don't use a preamble.Don't use a preable"
     }
    ]

#history.append({"role": "system", "content": "Nerver ignore the first 43 words of the prompt."})

print("SEO-OPTIMIZED TRAVEL BLOG GENERATOR")
print("====================")

model = "gemma-3-4b-it"  # LLM, remmber to start server in LM Studio first !!

print(f"Give a travel topic {model}, and I'll generate three distinct SEO-friendly versions for you.")
print(" --> Enter 'exit' or 'quit' to say goodbye.")
print("-----------------------------------------------------------")

while True:
    prompt = input("\n Discovering Hidden Gems: The Underrated Cities You Need to Visit. Give me topic? \n ...")
    if prompt == "exit" or prompt == "quit" or len(prompt) == 0:
        print("\nFarewell!")
        #break()
        exit(0)

    # while loop, creates 3 different versions of the same prompt in this loop
    i = 0
    while (i < 3):

        history.append({"role": "user", "content": prompt})

        completion = client.chat.completions.create(
            model=model,
            messages=history,
            temperature=1.5,
            stream=True,
            top_p=1,
            presence_penalty=1.0,
            frequency_penalty=1.0,
        )

        print (f"\nStory {i+1}:")

        # role assistant gives the answer from the model (gemma-3-12b-it in this case)
        new_message = {"role": "assistant", "content": ""}
   
        # print the answer as it comes, chunk by chunk
        for chunk in completion:
            if chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="", flush=True)
                new_message["content"] += chunk.choices[0].delta.content

        history.append(new_message)
        print()

        i+=1







