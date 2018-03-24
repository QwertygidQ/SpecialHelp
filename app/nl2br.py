# Taken from http://flask.pocoo.org/snippets/28/

import re
from . import app
from jinja2 import evalcontextfilter, Markup, escape

_paragraph_re = re.compile('\r\n|\r|\n')


@app.template_filter()
@evalcontextfilter
def nl2br(eval_ctx, value):
    lines = _paragraph_re.split(escape(value))
    result = '<br>\n'.join(lines)

    if eval_ctx.autoescape:
        result = Markup(result)
    return result
