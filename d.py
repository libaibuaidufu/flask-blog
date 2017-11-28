import jinja2 as jj


template_string = '''
{{- "there is a link: http://tieba.baidu.com/p/3697161800i&pn=3" | wordcount() }}
'''


t = jj.Template(template_string)
print t.render()