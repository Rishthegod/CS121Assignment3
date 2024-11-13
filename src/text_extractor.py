'''
Extracts text from an HTML file and returns the associated tags
'''



'''

<p>               <-- element
   some text      <-- this is a text node
   some text      <-- another text node
   <a>test</a>    <-- element with text node inside
   more text      <-- text node
</p>              <-- end of <p> element


output:  list[text, parent_element]
example: [
  ['some text', bs4.Element<p>],
  ['some text', bs4.Element<p>],
  ['test', bs4.Element<a>],
  ['more text', bs4.Element<p>]
]


Ignore <scripts>, Comments (<!-- text -->), and any hidden nodes (to the best of your ability)
refer to HW2 code if needed
'''

from bs4 import BeautifulSoup, Comment


def is_hidden(element):

    """Check commonly used CSS properties to determine if an element is hidden"""
    if 'style' in element.attrs:

        style = element.attrs['style'].lower()

        if "display:none" in style or "visibility:hidden" in style:
            return True
        
    return False
    
    
            

def extract_tokens(html):
    soup = BeautifulSoup(html, 'html.parser')
    tokens = []
    for element in soup.descendants:
        if isinstance(element, Comment):
            continue
        elif isinstance(element, str):
            parent = element.parent

            if is_hidden(parent):
                continue

            if parent.name in  ['script', 'meta', 'style']:
                continue
            
            text = element.strip()
            if text:
                tokens.append([text, parent])

    return tokens
        
        
def main():
    html = """
    <html>
        <head>
            <title>TutorialsPoint</title>
        </head>
        <body>
            <p>
                Hello World
            </p>
        </body>
    </html>
    """
    tokens = extract_tokens(html)
    for text, parent in tokens:
        print(f"Text: '{text}', Parent: <{parent.name}>")

if __name__ == '__main__':
    main()