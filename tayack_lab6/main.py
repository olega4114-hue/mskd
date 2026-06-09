import re

class Emark:
    def __init__(self, w=80, h=24):
        self.w = w
        self.h = h
        self.scr = [[' ' for _ in range(w)] for _ in range(h)]
        self.col_map = {0: 30, 1: 34, 2: 32, 3: 36, 4: 31, 5: 35, 6: 33, 7: 37}
    
    def parse_attrs(self, attrs_str):
        attrs = {}
        pat = r'(\w+)="([^"]*)"'
        for m in re.finditer(pat, attrs_str):
            attrs[m.group(1)] = m.group(2)
        return attrs
    
    def parse_doc(self, content):
        doc_pat = r'<document\s+([^>]*)>(.*?)</document>'
        m = re.search(doc_pat, content, re.DOTALL)
        if not m:
            raise ValueError('Нет тега <document>')
        
        doc_attrs = self.parse_attrs(m.group(1))
        doc_content = m.group(2)
        
        rows = int(doc_attrs.get('rows', self.h))
        cols = int(doc_attrs.get('columns', self.w))
        
        row_pats = re.finditer(r'<row\s*([^>]*)>(.*?)</row>', doc_content, re.DOTALL)
        
        cur_row = 0
        for row_m in row_pats:
            if cur_row >= rows:
                break
            
            row_attrs = self.parse_attrs(row_m.group(1))
            row_content = row_m.group(2)
            row_height = int(row_attrs.get('height', 1))
            
            col_pats = re.finditer(r'<col\s*([^>]*)>(.*?)</col>', row_content, re.DOTALL)
            
            cur_col = 0
            col_widths = []
            col_list = []
            
            for col_m in re.finditer(r'<col\s+([^>]*)>(.*?)</col>', row_content, re.DOTALL):
                col_list.append((col_m.group(1), col_m.group(2).strip()))
            
            for i, (col_attrs, col_text) in enumerate(col_list):
                if cur_col >= cols:
                    break
                
                attrs = self.parse_attrs(col_attrs)
                w = int(attrs.get('width', 0))
                if w == 0:
                    w = (self.w - sum(col_widths)) // (len(col_list) - i)
                
                col_widths.append(w)
                
                halign = attrs.get('halign', 'left')
                valign = attrs.get('valign', 'top')
                txt_col = int(attrs.get('textcolor', 15))
                bg_col = int(attrs.get('bgcolor', 0))
                
                for i in range(row_height):
                    if cur_row + i < self.h:
                        for j, ch in enumerate(col_text[:w]):
                            if cur_col + j < self.w:
                                self.scr[cur_row + i][cur_col + j] = ch
                
                cur_col += w
            
            cur_row += row_height
    
    def render(self):
        for row in self.scr:
            print(''.join(row))

def main():
    try:
        with open('document.emark', 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print('Ошибка: файл document.emark не найден')
        return
    
    try:
        em = Emark()
        em.parse_doc(content)
        em.render()
    except Exception as e:
        print(f'Ошибка: {e}')

if __name__ == '__main__':
    main()
