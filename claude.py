import anthropic, json, os, time
from typing import List, Tuple
from dotenv import load_dotenv
load_dotenv()

def get_txt(name: str) -> str:

    text_file = ''

    with open(name, 'r') as txt:

        text_file = txt.read()

    return text_file

prompt_body = get_txt('prompt.txt')
department_codes = get_txt('departments.txt')
missing = get_txt('missing.txt').split('\n')

course_data = None
with open('compiled_courses.json', 'r') as cc:
    course_data = json.load(cc)['courses']

# Filter out non relivant
for key, item in course_data.copy().items():

    num = key.split(' ')[-1].lower()

    if not num.isnumeric():

        course_data.pop(key)
    
    elif int(num) > 600:

        course_data.pop(key)
    
    elif not item['prereqtext']:

        course_data.pop(key)

print(course_data.__len__())

def assemble_prompt(targets: List[str], prompt: str = prompt_body, departments: str = department_codes) -> str:

    return '\n'.join([prompt, *[f'{i+1}. {t}' for i, t in enumerate(targets)], departments])

num_cases = 50
group_i = 1
courses = []
desc = []

client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key=os.getenv('CLAUDE_KEY'),
)

for i, (course_code, item) in enumerate(course_data.items()):

    print(i, end='\r')

    if not item['prereqtext']:

        continue

    for desc_item in item['prereqtext'].values():

        courses.append(course_code)
        desc.append(desc_item)

    if (courses.__len__() > num_cases or i+1 == course_data.__len__()):

        os.chdir('processed_courses/run3')

        try:

            path = f'group_{group_i}'

            os.mkdir(path)
            os.chdir(path)

            group_prompt = assemble_prompt(desc)

            with open('track.txt', 'w') as track:

                track.write('\n'.join(courses))

            with open('prompt.txt', 'w') as p_file:

                p_file.write(group_prompt)

            # Do model

            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=5000,
                temperature=0,
                system=f"""
                            <documents>
                            <document>
                            {group_prompt}
                            </document>
                            </documents>

                            You are a prerequisite parser. Use the above rules and department codes to help parse prerequisites. Return all 50 cases, do not under any circumstances say \"Would you like me to continue with the remaining cases?\"".
                        """,
                messages=[
                    {
                        "role": "user",
                        "content": "Complete the System Prompt"
                    },
                    {
                        "role": "user",
                        "content": "Complete the System Prompt"
                    }
                ]
            )

            message2 = None

            if message.content[0].text.count("{") < 40:

                message2 = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=5000,
                temperature=0,
                system=f"""
                            <documents>
                            <document>
                            {group_prompt}
                            </document>
                            </documents>

                            You are a prerequisite parser. Use the above rules and department codes to help parse prerequisites. Return all 50 cases, do not under any circumstances say \"Would you like me to continue with the remaining cases?\"".
                        """,
                messages=[
                    {
                        "role": "user",
                        "content": "Complete the System Prompt"
                    },
                    {
                        "role": "assistant",
                        "content": message.content[0].text
                    },
                    {
                        "role": "user",
                        "content": "Yes, continue with all the remaining cases"
                    }
                ]
            )

            # print(message.content)

            with open('response.txt', 'w') as resp:

                resp.write(message.content[0].text + (message2.content[0].text if message2 else ""))

            os.chdir('../')

        except FileExistsError as FE:

            pass

        os.chdir('../../')
        courses = []
        desc = []
        group_i += 1