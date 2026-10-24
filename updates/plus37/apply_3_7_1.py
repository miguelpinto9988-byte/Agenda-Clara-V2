from pathlib import Path
import shutil
src=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
main=src/"MainActivity.java"
s=main.read_text(encoding="utf8")
import re
shutil.copyfile("updates/plus37/TopPlusMotion.java",src/"TopPlusMotion.java")
# Actual 3.7 upper button: U+FF0B and openEditor, not openQuickActions.
needle='Button add=button("＋",()->openEditor(-1,null,null));add.setTag("new_task_button");'
assert s.count(needle)==1,"Upper plus button anchor missing"
s=s.replace(needle,'''Button add=button("＋",()->openEditor(-1,null,null));add.setTag("new_task_button");
        add.setOnClickListener(v->{
            v.animate().cancel();
            v.setPivotX(v.getWidth()/2f);v.setPivotY(v.getHeight()/2f);
            v.animate().rotation(45f).scaleX(.92f).scaleY(.92f).setDuration(125)
                .withEndAction(()->v.animate().rotation(0f).scaleX(1f).scaleY(1f)
                    .setDuration(280).setInterpolator(new android.view.animation.OvershootInterpolator(1.2f)).start()).start();
            openEditor(-1,null,null);
        });''',1)
# Repair legacy 3.7 template multiline Java literals before javac.
s=s.replace('día(s)\\n"+days;', 'día(s)\\\\n"+days;')
s=s.replace('calendar.account+"\\nCalendario:', 'calendar.account+"\\\\nCalendario:')
s=s.replace('calendar.name+"\\nBloques propuestos:', 'calendar.name+"\\\\nBloques propuestos:')
s=s.replace('total+"\\nPosibles duplicados:', 'total+"\\\\nPosibles duplicados:')
s=s.replace('duplicates+".\\n\\nSe importarán', 'duplicates+".\\\\n\\\\nSe importarán')
# Normalize accidental literal newlines introduced by earlier 3.7 templates.
# Java regular string literals must use escaped newline sequences.
out=[]
in_string=False
in_char=False
in_line_comment=False
in_block_comment=False
escaped=False
i=0
fixed=0
while i<len(s):
    ch=s[i]
    nxt=s[i+1] if i+1<len(s) else ''
    if in_line_comment:
        out.append(ch)
        if ch=='\\n': in_line_comment=False
    elif in_block_comment:
        out.append(ch)
        if ch=='*' and nxt=='/':
            out.append('/');i+=1;in_block_comment=False
    elif in_string:
        if ch=='\\n':
            out.append('\\\\n')
            fixed+=1
            escaped=False
        else:
            out.append(ch)
            if escaped: escaped=False
            elif ch=='\\\\': escaped=True
            elif ch=='"': in_string=False
    elif in_char:
        out.append(ch)
        if escaped: escaped=False
        elif ch=='\\\\': escaped=True
        elif ch=="'": in_char=False
    elif ch=='/' and nxt=='/':
        out.extend(['/', '/']);i+=1;in_line_comment=True
    elif ch=='/' and nxt=='*':
        out.extend(['/', '*']);i+=1;in_block_comment=True
    elif ch=='"':
        out.append(ch);in_string=True
    elif ch=="'":
        out.append(ch);in_char=True
    else: out.append(ch)
    i+=1
s=''.join(out)
print("Normalized Java literal line breaks:",fixed,flush=True)
assert not in_string and not in_char,"Unterminated Java literal"
main.write_text(s,encoding="utf8")
gradle=Path("AgendaClara/app/build.gradle")
g=gradle.read_text(encoding="utf8")
assert "versionCode 27" in g and "versionName '3.7.0'" in g
gradle.write_text(g.replace("versionCode 27","versionCode 28").replace("versionName '3.7.0'","versionName '3.7.1'"),encoding="utf8")
print("PASS: centered top plus motion installed over 3.7, version 3.7.1")
