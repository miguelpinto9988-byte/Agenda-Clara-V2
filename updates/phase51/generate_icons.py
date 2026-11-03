#!/usr/bin/env python3
"""Generate 328 matte multi-color transparent PNG assets at build time.
Individual objects have natural varied pigments, not glossy badges or shared shiny backplates.
No emojis, fonts, or externally licensed graphics are bundled.
"""
from pathlib import Path
import math, sys, json, re
from PIL import Image, ImageDraw, ImageFilter, ImageFont

DEST = Path(sys.argv[1]) if len(sys.argv)>1 else Path('AgendaClara/app/src/main/res/drawable-nodpi')
DEST.mkdir(parents=True,exist_ok=True)
DATA = {
 'math': 'matematicas algebra geometria calculo aritmetica estadistica trigonometria probabilidad logica matematicas_discretas analisis_numerico ecuaciones',
 'flask': 'quimica bioquimica laboratorio farmaceutica ciencias_experimentales quimica_organica quimica_inorganica materiales biotecnologia toxologia',
 'atom': 'fisica fisica_cuantica mecanica termodinamica electromagnetismo optica electricidad energia astronomia astrofisica',
 'leaf': 'biologia botanica ecologia ambiente ciencias_naturales zoologia microbiologia evolucion agricultura genetica biodiversidad',
 'book': 'literatura lectura escritura comprension_lectora poesia novela cuentos lengua_castellana comunicacion textos_liricos linguistica',
 'scroll': 'historia historia_universal historia_del_peru arqueologia patrimonio cronologia antropologia historia_moderna cultura civilizaciones',
 'globe': 'geografia cartografia geologia ciencias_sociales social_studies paises territorios clima mundo geografia_fisica turismo',
 'chat': 'ingles frances aleman portugues italiano idiomas traduccion idiomas_extranjeros oralidad debate oratoria',
 'laptop': 'informatica computacion programacion software hardware sistemas bases_de_datos redes ciberseguridad desarrollo_web algoritmos',
 'palette': 'arte pintura dibujo fotografia diseno artes_visuales teatro cine escultura creatividad diseno_grafico arquitectura',
 'music': 'musica coro piano guitarra musica_instrumental armonia composicion danza folclore sonido educacion_musical',
 'brain': 'psicologia neurociencia neuroeducacion memoria aprendizaje cognicion filosofia etica pensamiento psicologia_social salud_mental',
 'scales': 'derecho civica ciudadania politicas ciudadania_global legislacion relaciones_internacionales justicia democracia normas',
 'chart': 'economia contabilidad finanzas emprendimiento administracion marketing gestion comercio negocios inversiones recursos_humanos',
 'heart': 'medicina enfermeria salud anatomia fisiologia nutricion epidemiologia primeros_auxilios bienestar terapia odontologia',
 'grad': 'educacion pedagogia didactica tutoria_educativa evaluacion_curricular practica_docente estrategias_educativas docencia formacion orientacion',
 'gear': 'ingenieria ingenieria_mecanica automatizacion mecatronica robotica procesos industriales fabricacion tecnologia control',
 'scope': 'investigacion tesis metodologia investigacion_educativa trabajo_de_campo experimentos analisis_de_datos proyecto_cientifico encuestas laboratorio_cientifico',
 'ball': 'deporte futbol baloncesto voleibol atletismo natacion educacion_fisica gimnasia entrenamiento competicion recreacion',
 'clock': 'horario calendario tiempo cronograma planificacion agenda turnos rutina sesiones puntualidad fecha_limite',
 'pencil': 'tarea examen evaluacion parcial final practica trabajo informe ensayo actividad notas apuntes resumen presentacion exposicion proyecto',
 'star': 'prioridad objetivo logro meta recordatorio alarma evento reunion tutorias seminario taller lecturas actividad_especial',
 'tools': 'construccion diseno_industrial dibujo_tecnico mecanica_aplicada taller_mecanico instalaciones logistica manufactura electronica',
 'camera': 'fotografia_profesional video imagenes multimedia audiovisual produccion_digital edicion_video cine_documental comunicacion_digital',
 'plant': 'jardineria agricultura_urbana suelos forestal desarrollo_sostenible energias_renovables huertos medioambiente',
 'food': 'gastronomia cocina reposteria alimentos alimentacion seguridad_alimentaria industria_alimentaria hoteleria',
 'people': 'sociologia sociedad trabajo_en_equipo liderazgo emprendimiento_social comunidad grupos colaboracion recursos_sociales',
 'light': 'ideas innovacion proyecto_creativo resolucion_de_problemas pensamiento_critico tecnologia_educativa creatividad_digital',
 'folder': 'documento documentos pdf archivos carpeta carpeta_de_clase syllabus silabo biblioteca repositorio recursos',
 'bell': 'notificacion aviso alarma_recordatorio vencimiento actividad_pendiente seguimiento aviso_importante',
 'location': 'aula campus laboratorio_aula edificio lugar viaje excursion trabajo_de_campo_geografico biblioteca_universitaria',
 'general': 'general otros sin_categoria categoria_personalizada curso_desconocido tarea_general actividad_general',
}
PALETTES=[((108,58,239),(207,104,252)),((0,182,242),(45,122,238)),((9,199,164),(36,235,223)),((248,113,39),(255,200,71)),((249,61,130),(255,142,200)),((74,173,58),(140,231,75)),((85,76,228),(131,174,255)),((234,89,180),(152,84,246))]
# The family drawing, not arbitrary coloring of a single glyph, defines the semantic subject.

def glyph(d,kind):
    dark=(28,33,87,240)
    if kind in ('book','scroll','folder','grad'):
        if kind=='book':
            # A stack of distinctly colored physical books: teal, yellow, coral.
            colors=[(24,171,117,255),(246,186,57,255),(228,91,89,255)]
            for k,color in enumerate(colors):
                top=116-k*29
                d.polygon([(43,top+7),(132,top),(150,top+12),(61,top+19)],fill=color)
                d.polygon([(61,top+19),(150,top+12),(150,top+25),(61,top+32)],fill=tuple(max(0,int(c*.82)) for c in color[:3])+(255,))
                d.polygon([(45,top+12),(61,top+19),(61,top+32),(45,top+25)],fill=(246,244,229,255))
                d.line([(44,top+11),(132,top+4),(148,top+14)],fill=(51,65,87,235),width=2)
        elif kind=='grad':
            d.polygon([(33,81),(98,47),(159,81),(97,114)],fill=(50,106,186,255),outline=(49,66,88,235))
            d.polygon([(64,100),(126,100),(126,123),(64,123)],fill=(126,81,166,255))
            d.arc((63,110,127,138),5,175,fill=(58,64,91,255),width=4)
            d.line([(148,84),(148,120)],fill=(230,169,54,255),width=5)
        elif kind=='folder':
            d.rounded_rectangle((38,78,149,140),radius=8,fill=(234,180,50,255),outline=(61,73,94,230),width=3)
            d.polygon([(40,76),(93,76),(103,89),(145,89),(145,109),(40,109)],fill=(250,203,84,255))
        else:
            d.rounded_rectangle((58,49,135,146),radius=7,fill=(240,208,143,255),outline=(90,69,73,240),width=3)
            d.line([(74,76),(119,76)],fill=(175,77,64,255),width=5)
            d.line([(74,95),(119,95)],fill=(128,103,80,255),width=4)
            d.line([(74,114),(111,114)],fill=(128,103,80,255),width=4)
    elif kind in ('flask','atom','scope','plant'):
        if kind=='atom':
            for a in [-45,0,45]:
                # rotated orbital ellipse as polyline
                points=[]
                for i in range(60):
                    t=2*math.pi*i/59
                    x,y=math.cos(t)*53,math.sin(t)*21
                    r=math.radians(a);points.append((96+x*math.cos(r)-y*math.sin(r),97+x*math.sin(r)+y*math.cos(r)))
                d.line(points,fill=(255,255,255,255),width=4,joint='curve')
            d.ellipse((88,89,104,105),fill=(255,223,40,255),outline=dark,width=2)
        elif kind=='scope':
            d.ellipse((73,67,120,113),fill=(255,255,255,248),outline=dark,width=4)
            d.line(((113,111),(137,138)),fill=(255,214,65,255),width=12)
        elif kind=='plant':
            d.line(((99,143),(99,78)),fill=(15,130,91,255),width=6)
            d.ellipse((66,74,99,110),fill=(20,230,137,255),outline=dark,width=3)
            d.ellipse((99,59,129,96),fill=(70,241,145,255),outline=dark,width=3)
        else:
            d.polygon([(81,54),(110,54),(110,88),(133,134),(57,134),(81,88)],fill=(241,250,255,251),outline=dark)
            d.polygon([(70,108),(120,108),(132,134),(58,134)],fill=(42,235,204,240))
            d.line(((76,55),(114,55)),fill=dark,width=5)
    elif kind in ('math','chart','gear','laptop','tools'):
        if kind=='math':
            d.rounded_rectangle((52,54,140,141),radius=13,fill=(242,249,255,255),outline=dark,width=5)
            d.rounded_rectangle((63,67,130,88),radius=4,fill=(13,186,223,240))
            for x in (67,91,115):
                for y in (101,122):d.rounded_rectangle((x,y,x+13,y+12),radius=2,fill=(142,83,251,240))
        elif kind=='laptop':
            d.rounded_rectangle((54,62,137,123),radius=5,fill=(240,250,255,250),outline=dark,width=5)
            d.polygon([(47,128),(145,128),(136,140),(56,140)],fill=(28,220,254,255),outline=dark)
            d.line(((73,94),(86,82),(73,82)),fill=(31,105,217,250),width=5)
        elif kind=='chart':
            for i,h in enumerate([24,53,43,65]):d.rounded_rectangle((61+i*22,139-h,75+i*22,140),radius=4,fill=(255,246,194,255))
            d.line([(54,142),(54,65)],fill=dark,width=4)
        elif kind=='tools':
            d.line(((58,132),(133,63)),fill=(244,239,255,255),width=14)
            d.ellipse((110,55,141,85),outline=dark,width=5)
        else:
            d.ellipse((64,65,128,129),outline=(245,248,255,255),width=17)
            d.ellipse((88,88,105,105),fill=(255,196,70,255))
    elif kind in ('leaf','globe','location','ball','heart'):
        if kind=='globe':
            d.ellipse((52,54,140,141),fill=(62,210,247,251),outline=dark,width=4)
            d.ellipse((78,54,112,141),outline=(247,250,255,255),width=4)
            d.line(((52,97),(140,97)),fill=(250,255,255,250),width=4)
        elif kind=='ball':
            d.ellipse((57,59,137,139),fill=(247,252,255,254),outline=dark,width=4)
            d.polygon([(96,85),(110,96),(106,115),(85,115),(80,97)],fill=dark)
        elif kind=='heart':
            d.polygon([(96,132),(62,100),(64,78),(79,71),(96,83),(114,71),(132,79),(132,101)],fill=(254,72,119,255),outline=dark)
            d.line(((58,103),(83,103),(92,91),(100,114),(110,100),(137,100)),fill=(250,252,255,255),width=4)
        elif kind=='location':
            d.ellipse((65,56,127,118),fill=(254,241,255,252),outline=dark,width=5)
            d.polygon([(66,106),(127,106),(96,149)],fill=(254,241,255,252),outline=dark)
            d.ellipse((85,78,106,99),fill=(100,128,246,255))
        else:
            d.ellipse((55,63,140,128),fill=(34,229,135,245),outline=dark,width=3)
            d.line(((70,119),(121,77)),fill=(245,255,239,245),width=5)
    elif kind in ('pencil','scroll','camera','food'):
        if kind=='camera':
            d.rounded_rectangle((51,75,140,129),radius=11,fill=(245,250,255,251),outline=dark,width=5)
            d.ellipse((81,84,116,119),fill=(40,195,245,255),outline=dark,width=4)
        elif kind=='food':
            d.ellipse((56,74,139,133),fill=(255,249,240,250),outline=dark,width=5)
            d.line(((75,58),(75,116)),fill=(255,209,40,255),width=5)
        else:
            d.rounded_rectangle((57,57,133,137),radius=11,fill=(245,251,255,251),outline=dark,width=4)
            for y in [77,96,115]:d.line(((72,y),(119,y)),fill=(103,105,215,255),width=5)
            d.line(((115,125),(142,87)),fill=(254,183,41,255),width=9)
    elif kind in ('chat','brain','people','music','scales'):
        if kind=='brain':
            d.ellipse((57,57,136,132),fill=(253,162,208,254),outline=dark,width=5)
            for x in (80,96,112):d.arc((x-17,69,x+17,105),200,450,fill=(247,243,255,255),width=4)
        elif kind=='music':
            d.line(((93,72),(93,123)),fill=(247,249,255,255),width=10)
            d.line(((93,74),(128,64)),fill=(247,249,255,255),width=6)
            d.ellipse((62,115,95,134),fill=(249,252,255,255),outline=dark,width=3)
        elif kind=='scales':
            d.line(((96,59),(96,139)),fill=(245,252,255,255),width=6)
            d.line(((56,80),(136,80)),fill=(245,252,255,255),width=5)
            d.polygon([(54,84),(73,84),(82,115),(48,115)],fill=(251,201,78,255))
            d.polygon([(114,84),(134,84),(143,115),(106,115)],fill=(251,201,78,255))
        elif kind=='people':
            for x in (72,120):
                d.ellipse((x-12,64,x+12,88),fill=(255,241,251,255))
                d.rounded_rectangle((x-20,94,x+20,135),radius=12,fill=(255,241,251,248))
        else:
            d.rounded_rectangle((48,61,144,122),radius=19,fill=(251,250,255,253),outline=dark,width=4)
            d.polygon([(68,119),(67,141),(91,119)],fill=(252,251,255,253))
            d.line(((67,85),(125,85)),fill=(48,153,239,255),width=5)
    elif kind in ('bell','clock','star','light'):
        if kind=='bell':
            d.pieslice((63,61,130,130),180,360,fill=(255,220,42,255),outline=dark,width=4)
            d.rectangle((62,96,131,127),fill=(255,220,42,255),outline=dark,width=3)
            d.ellipse((88,126,106,141),fill=(252,149,56,255))
        elif kind=='clock':
            d.ellipse((53,53,139,140),fill=(252,251,255,255),outline=dark,width=5)
            d.line(((96,70),(96,99),(120,108)),fill=(49,96,213,255),width=6)
        elif kind=='light':
            d.ellipse((62,56,132,123),fill=(251,237,116,255),outline=dark,width=5)
            d.rounded_rectangle((80,113,115,140),radius=7,fill=(255,250,249,255),outline=dark,width=4)
        else:
            pts=[]
            for i in range(10):
                a=-math.pi/2+i*math.pi/5;r=51 if i%2==0 else 22
                pts.append((96+int(r*math.cos(a)),99+int(r*math.sin(a))))
            d.polygon(pts,fill=(255,226,82,255),outline=dark)
    elif kind=='palette':
        d.ellipse((42,58,145,133),fill=(223,177,105,255),outline=(88,78,72,255),width=3)
        d.ellipse((91,94,119,120),fill=(255,250,235,255))
        for x,y,color in [(69,75,(227,79,90,255)),(94,66,(61,143,205,255)),(121,78,(55,174,111,255)),(62,105,(164,91,195,255))]:
            d.ellipse((x-10,y-10,x+10,y+10),fill=color)
        d.line(((132,136),(152,84)),fill=(142,90,55,255),width=8)
    elif kind=='general':
        d.rounded_rectangle((49,57,144,136),radius=17,fill=(249,249,240,255),outline=dark,width=4)
        for x,y,color in [(63,68,(63,165,199,255)),(102,68,(237,180,64,255)),(63,106,(58,174,120,255)),(102,106,(207,103,144,255))]:
            d.rounded_rectangle((x,y,x+28,y+22),radius=4,fill=color)
    else:
        d.rounded_rectangle((52,56,140,139),radius=19,fill=(251,249,255,251),outline=dark,width=5)
        d.ellipse((76,81,117,119),fill=(254,201,86,255))

# Icon art: transparent outside objects, gentle contact shadow, NO glossy background orb,
# no specular white ellipse, no neon rim or uniform purple/blue tint.
catalog={}; total=0; icon_count=0
all_keys=[]
for family,keys in DATA.items():
    for i,key in enumerate(keys.split()):
        identifier='ic_adapt_'+key
        if not re.fullmatch(r'ic_adapt_[a-z0-9_]+',identifier):raise ValueError(identifier)
        if key in catalog:raise ValueError('Duplicated icon '+identifier)
        s=192;hi=2;size=s*hi
        bg=Image.new('RGBA',(size,size),(0,0,0,0))
        # Restrained object shadow; keeps original background transparent.
        shadow=Image.new('RGBA',(size,size),(0,0,0,0));sd=ImageDraw.Draw(shadow)
        sd.ellipse((92,290,292,324),fill=(30,39,66,35))
        bg.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(12)))
        drawing=Image.new('RGBA',(192,192),(0,0,0,0));g=ImageDraw.Draw(drawing)
        glyph(g,family)
        # Small, deterministic variations of the object pigments for each subject.
        # No shiny shared tile, background halo or white specular highlights.
        alpha=drawing.getchannel('A')
        h,sat,val=drawing.convert('RGB').convert('HSV').split()
        shift=(i*7+sum(ord(c) for c in family)*3)%31-15
        h=h.point(lambda v: (v+shift)%256)
        adjusted=Image.merge('HSV',(h,sat,val)).convert('RGB')
        adjusted.putalpha(alpha);drawing=adjusted
        bg.alpha_composite(drawing.resize((size,size),Image.Resampling.LANCZOS))
        out=bg.resize((s,s),Image.Resampling.LANCZOS)
        path=DEST/(identifier+'.png');out.save(path,optimize=True,compress_level=9)
        total+=path.stat().st_size;icon_count+=1;catalog[key]={'family':family,'file':identifier+'.png'}
        all_keys.append(key)
assert total<=15*1024*1024,(total,'exceeds 15MB budget')
assert icon_count>=300,icon_count
meta=DEST.parent.parent/'assets/adaptive_icon_catalog.json';meta.parent.mkdir(parents=True,exist_ok=True)
meta.write_text(json.dumps({'count':icon_count,'png_bytes':total,'budget_bytes':15*1024*1024,'style':'matte-multicolor-transparent','icons':catalog},ensure_ascii=False,sort_keys=True),encoding='utf-8')
# An exhaustive key catalog provides a resource candidate for every entry, not just 30 aliases.
java=DEST.parent.parent/'java/pe/agendaclara/app/AdaptiveIconIndex.java'
java.parent.mkdir(parents=True,exist_ok=True)
by_length=sorted(all_keys,key=lambda k:(-len(k),k))
chunks=[by_length[i:i+14] for i in range(0,len(by_length),14)]
lines=['package pe.agendaclara.app;','/** Generated index of bundled matte PNG themes. Internal application resource. */','final class AdaptiveIconIndex {',' private AdaptiveIconIndex(){}',' static final String[] KEYS = {']
for part in chunks:lines.append('   '+','.join('"'+key+'"' for key in part)+',')
lines.extend([' };','}'])
java.write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('PASS matte adaptive icon library: %d original PNG images, %d bytes / %d budget'%(icon_count,total,15*1024*1024))
