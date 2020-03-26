import re, regex, os
from sys import argv
from xml.etree.ElementTree import fromstring
from xml.sax.saxutils import escape, unescape
import json

with open('dxml.config.json', 'r') as config_file:
    data = config_file.read()
    try:
        config = json.loads(data)
    except Exception as e:
        print("failed to load config file, please check if the json data are formatted correctly")
        print(e)
        exit(-1)


def compatible_custom(element, parent):
    if element.tag in config['CUSTOM_WIDGETS'][parent.tag]:
        tag = element.tag
        element.tag = config['CUSTOM_WIDGETS'][parent.tag][element.tag]
        return [tag, xml2widget(element.getchildren(), element)]

    return [element.tag, xml2widget(element.getchildren(), element, move_on=True)]

def is_list_widget(widget):
    
    if 'x-list' in widget.attrib:
        if widget.attrib['x-list'].strip() == 'true':
            widget.attrib.pop('x-list')
            return True

        widget.attrib.pop('x-list')
    return False

def xml2widget(elements, parent, move_on=False):
    
    try:
        if parent.tag in config['NO_CHILD_WIDGETS']:
            
            if config['NO_CHILD_WIDGETS'][parent.tag]:
                
                if 'x-value' not in parent.attrib:
                    
                    return "%s(\n %s, %s)"%(parent.tag,
                            ':'.join([config['NO_CHILD_WIDGETS'][parent.tag], '"{}"'.format(parent.text)]),
                            ',\n'.join([':'.join([i, parent.attrib[i]]) for i in parent.attrib])
                        )
                else:
                    
                    value = parent.attrib.pop('x-value')
                    return "%s(%s, %s)"%(
                        parent.tag,
                         '%s: %s'%(config['NO_CHILD_WIDGETS'][parent.tag], value),
                         ',\n'.join([':'.join([i, parent.attrib[i]]) for i in parent.attrib])
                        )
            else:
                
                if 'x-value' not in parent.attrib:
                    
                    if type(parent.text) != type(None):
                        
                        return '%s("%s", %s)'%(
                            parent.tag,
                            parent.text.strip(),
                            ',\n'.join([':'.join(i) for i in parent.items()])
                            )
                    else:
                    
                        return '%s("", %s)'%(
                            parent.tag,
                            ',\n'.join([':'.join(i) for i in parent.items()])
                            )
                else:
                
                    value = parent.attrib.pop('x-value')
                    return '%s(%s, %s)'%(
                        parent.tag,
                        value,
                        ',\n'.join([':'.join(i) for i in parent.items()])
                        )

        
        elif parent.tag in config['CUSTOM_WIDGETS']:
        
            return "%s(\n %s %s %s)"%(
                    parent.tag,
                    ',\n'.join(['{}:{}'.format(*compatible_custom(element, parent)) for element in elements]),
                    ',' if len(elements) > 0 else '',
                    ',\n'.join([':'.join(item) for item in parent.items()])
                    )

        else:
        
            if not move_on:
                
                if is_list_widget(parent) or len(elements) > 1 or parent.tag in config['LIST_WIDGETS']:
                    
                    if 'x-field' in parent.attrib:
                        field = parent.attrib.pop('x-field').replace("'", '')
                    else:
                        field = 'children' if parent.tag not in config['LIST_WIDGETS'] else config['LIST_WIDGETS'][parent.tag]
                    return '%s(\n %s: [%s], %s)'%(parent.tag,
                             field,
                            ',\n'.join([xml2widget(i.getchildren(), i) for i in elements]),
                            ',\n'.join([':'.join(i) for i in parent.items()])
                        )
                elif len(elements) == 1:
                    
                    if 'x-field' in parent.attrib:
                        field = parent.attrib.pop('x-field').replace("'", '')
                    else:
                        field = 'child'
                    return '%s(%s: %s, %s)'%(parent.tag,field,
                     xml2widget(elements[0].getchildren(), elements[0]),
                        ',\n'.join([':'.join(i) for i in parent.items()])
                        )
                else:
                    
                    if type(parent.text) != type(None):
                        
                        if parent.text.strip():
                            
                            return '%s("%s", %s)'%(parent.tag, parent.text,',\n'.join([':'.join(i) for i in parent.items()]))

                    return '%s(%s)'%(parent.tag, ',\n'.join([':'.join(i) for i in parent.items()]))
            else:
                if is_list_widget(parent) or len(elements) > 1 or parent.tag in config['LIST_WIDGETS']:
                    return '[%s]'%(
                            ',\n'.join([xml2widget(i.getchildren(), i) for i in elements]),
                        )
                elif len(elements) == 1:
                    
                    return '%s'%(
                     xml2widget(elements[0].getchildren(), elements[0])
                        )
                return 'null'

    except Exception as e:
        print("error while compiling widget '%s'"%parent.tag)
        if elements:
            print("whose children are '" + ', '.join([i.tag for i in elements]) + "'")

        print(e)
        exit(-1)

def compile_tree(tree):
    try:
        xml_tree = ''.join(tree)
        embedded_dart = re.findall(r'(\{\|(.*?)\|\})', xml_tree)
        for dart in embedded_dart:
            xml_tree = xml_tree.replace(dart[0], '<__embedded-dart__/>')
        element = fromstring(xml_tree)
    except Exception as e:
        
        print('error while compiling xml at')
        print('*'*50)
        print(''.join(tree).replace('<!--new_line-->','\n'))
        print('*'*50)
        print(e)
        exit(-1)

    widget = xml2widget(element.getchildren(), element)
    for embedded in embedded_dart:
        widget = widget.replace('__embedded-dart__("", )', embedded[1], 1)
    return unescape(widget)

def cleaned(suspects): # to avoid generic classess being included
    cleaned_elements = []
    for suspect in suspects:
        if re.match('<{}(\s+)*>'.format(suspect[1]), suspect[0]):
            new_test = suspect[0].replace('<%s'%suspect[1], '', 1)
            cleaned_elements += cleaned(re.findall(r'(<([a-zA-Z_0-9\.]+)(.*)/>)', new_test))
        else:
            cleaned_elements += [suspect]
    return cleaned_elements

def compileDXML(code):
    
    code = code.replace('\n', '<!--new_line-->')

    trees_heads = re.findall(r'<(\s)*([a-zA-Z_0-9\.]+)(\s+([a-zA-Z_0-9\.\-]+)=\{\%(.*?)\%\})(\s)*(/>|>)',code)
    for i, head in enumerate(trees_heads):
        # converting dxml into xml to be able to analyze easly !
        head = list(head)
        head[2] = escape(re.sub(r'([a-zA-Z_0-9\.\-]+)=\{\%(.*?)\%\}', r'\1="\2"', head[2].replace('"', "'")),
            {'<': '&lt;','>': '&gt;','&': '&amp;'})

        code = code.replace(trees_heads[i][2], head[2], 1)
    trees = re.findall(r'(<([a-zA-Z_0-9\.]+)(.*?)>)(.*?)(</\2>)', code)
    while trees:
        for tree in trees:
            tree = list(tree)
            tree.pop(2)
            tree.pop(1)
            
            code = code.replace(''.join(tree), compile_tree(tree))
        trees = re.findall(r'(<([a-zA-Z_0-9\.]+)(.*?)>)(.*?)(</\2>)', code)

    self_enclosed = cleaned(re.findall(r'(<([a-zA-Z_0-9\.]+)(.*)/>)', code))
    while self_enclosed:
        for tag in self_enclosed:
            code = code.replace(tag[0], compile_tree(tag[0]))
        self_enclosed = re.findall(r'(<([a-zA-Z_0-9\.]+)(.*?)/>)', code)

    return code.replace('<!--new_line-->', '\n')


def create_dart_files(path, files):
    dart_files = []
    for i in range(len(files)):
        with open(path+'/'+files[i], 'r') as dxml_file:
            print("compiling %s"%(path+'/'+files[i]))
            dart_code = compileDXML(dxml_file.read())

        with open(path+'/'+files[i].split('.')[0]+'.dart', 'w+') as new_dart_file:
            new_dart_file.write(dart_code)
            print("%s compiled successfully"%(path+'/'+files[i]))




def compile_files_in_directory(directory):
    inner_directories = []
    files = []

    for item in os.listdir(directory):
        if item.endswith('.dxml'):
            files += [item]
        elif item.find('.') == -1:
            inner_directories += [item]

    create_dart_files(directory, files)
    for folder in inner_directories:
        compile_files_in_directory(directory+'/'+folder)


if __name__ == '__main__':
    path = argv.pop(1)
    compile_files_in_directory(path)
    for arg in argv:
        if arg == '--run':
            os.system('flutter run')


    


    
