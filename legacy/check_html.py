import html.parser
class HTMLChecker(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.void_tags = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr', '!doctype'}
    def handle_starttag(self, tag, attrs):
        if tag.lower() not in self.void_tags:
            self.stack.append((tag, self.getpos()))
    def handle_endtag(self, tag):
        if tag.lower() not in self.void_tags:
            if not self.stack:
                print(f'Error: closing </{tag}> without opening tag at line {self.getpos()[0]}')
            elif self.stack[-1][0].lower() == tag.lower():
                self.stack.pop()
            else:
                # find if it matches an earlier tag
                found = False
                for i in range(len(self.stack)-1, -1, -1):
                    if self.stack[i][0].lower() == tag.lower():
                        found = True
                        print(f'Error: closing </{tag}> at line {self.getpos()[0]} matches <{self.stack[i][0]}> from line {self.stack[i][1][0]} but there are unclosed tags inside: {[t[0] for t in self.stack[i+1:]]}')
                        self.stack = self.stack[:i]
                        break
                if not found:
                    print(f'Error: closing </{tag}> at line {self.getpos()[0]} has no matching open tag')
    def close(self):
        super().close()
        for tag, pos in self.stack:
            print(f'Error: unclosed <{tag}> from line {pos[0]}')
with open('index.html', 'r', encoding='utf-8') as f:
    checker = HTMLChecker()
    checker.feed(f.read())
    checker.close()
