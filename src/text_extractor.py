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
    """
    Determines whether an HTML element is hidden based on its style attributes or tag type.

    Parameters:
    - element (bs4.element.Tag): The HTML element to check.

    Returns:
    - bool: True if the element is considered hidden, False otherwise.

    An element is considered hidden if:
    - It has a 'style' attribute containing 'display:none' or 'visibility:hidden'.
    - It is an <input> element with type 'hidden'.
    """


    # Check commonly used CSS properties to determine if an element is hidden
    if 'style' in element.attrs:
        style = element.attrs['style'].lower().replace(': ', ':')
        if "display:none" in style or "visibility:hidden" in style:
            return True
    
    if 'hidden' in element.attrs: return True
        
    return False
    
    
            

def extract_tokens(html):
    """
    Extracts text from an HTML string and returns a list of [text, parent_element] pairs.

    Parameters:
    - html (str): The HTML content as a string.

    Returns:
    - List[List[str, bs4.element.Tag]]: A list where each item is a list containing:
        - text (str): The extracted text content.
        - parent_element (bs4.element.Tag): The parent HTML element of the text.

    The function ignores:
    - Comments (<!-- -->)
    - Text within <script>, <style>, and <meta> tags
    - Hidden elements (e.g., elements with 'display:none' or 'visibility:hidden' styles)
    - Empty strings after stripping whitespace
    """

    soup = BeautifulSoup(html, 'html.parser')
    tokens = []
    for element in soup.descendants:
        if isinstance(element, Comment):
            continue
        elif isinstance(element, str):
            parent = element.parent

            if is_hidden(parent):
                continue

            if parent.name in ['script', 'meta', 'style']:
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
        
    html2 = '''
    <html>
        <head>
            <title>Sample Title</title>
            <script type="text/javascript">
                var x = 1;
            </script>
            <style>.hide { display: none }</style>
        </head>
        <body>
            <!-- This is a comment -->
            <p>Visible text</p>
            <p style="display:none;">Hidden text</p>
            <p style="visibility:hidden;">Also hidden text</p>
            <div>
                <p class="hide">hidden by css, but if it shows up then whatever</p>
                Text inside div
                <p hidden>oh noes this is hidden</p>
                <a>nested visible text</a>
                <input type="hidden" value="secret"/>
                <input type="text" value="visible input"/>
            </div>
            <script>const y = 2;</script>
        </body>
    </html>
    '''
    print("\nTest Case 2:")
    tokens2 = extract_tokens(html2)
    for text, parent in tokens2:
        print(f"Text: '{text}', Parent: <{parent.name}>")
    

if __name__ == '__main__':
    main()