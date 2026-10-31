#!/usr/bin/env python3
"""Agenda Clara 3.9.5: conservative, local WhatsApp multi-activity/context prototype.
Apply once after phase34; never touches user databases, credentials or permissions.
"""
from pathlib import Path
import shutil
SRC=Path('AgendaClara/app/src/main/java/pe/agendaclara/app')
STAGE=Path(__file__).resolve().parent
BUILD=Path('AgendaClara/app/build.gradle')

def one(source, old, new, label):
    count=source.count(old)
    if count!=1:
        raise RuntimeError(f'phase35 {label}: expected one source anchor; found {count}')
    return source.replace(old,new,1)

def apply():
    original=(SRC/'MessageParser.java').read_text(encoding='utf-8')
    analyzer=(SRC/'ConversationAnalyzer.java').read_text(encoding='utf-8')
    gradle=BUILD.read_text(encoding='utf-8')
    original=one(original,
        '        // Each distinct activity is reviewed independently. Never create tasks automatically.',
        '''        // Extract independent activities while retaining multi-line continuation fallback.
        // Each proposal remains subject to explicit review; no task is created here.
        List<String> pieces=WhatsAppUnderstandingEngine.split(bounded);
        if(pieces.size()>1){
            List<Proposal> independent=new ArrayList<>();
            int validCount=0;
            for(String piece:pieces){
                Proposal candidate=parseOne(piece,now,zone,manual);
                if(!candidate.action)continue;
                validCount++;
                boolean repeated=false;
                for(Proposal prior:independent){
                    if(WhatsAppUnderstandingEngine.related(prior.original,candidate.original)
                        && prior.dateKnown==candidate.dateKnown
                        && (!prior.dateKnown||prior.due==candidate.due)){
                        repeated=true;break;
                    }
                }
                if(!repeated)independent.add(candidate);
                if(independent.size()==40)break;
            }
            if(validCount>1)return independent;
        }
        // Each distinct activity is reviewed independently. Never create tasks automatically.''',
        'multiple independent instructions')
    analyzer=one(analyzer,
        '        return out;\n    }\n}',
        '''        List<Finding> grouped=WhatsAppUnderstandingEngine.merge(out);
        WhatsAppUnderstandingEngine.applyCorrections(grouped,ordered,zone);
        return grouped;
    }
}''','context grouping and explicit corrections')
    gradle=one(gradle,'versionCode 35','versionCode 36','version code')
    gradle=one(gradle,"versionName '3.9.4'","versionName '3.9.5'",'version label')
    java_target=SRC/'WhatsAppUnderstandingEngine.java'
    if java_target.exists():
        raise RuntimeError('Refusing to overwrite existing understanding engine')
    if not (STAGE/'WhatsAppUnderstandingEngine.java').is_file():
        raise RuntimeError('Required understanding engine missing')
    (SRC/'MessageParser.java').write_text(original,encoding='utf-8')
    (SRC/'ConversationAnalyzer.java').write_text(analyzer,encoding='utf-8')
    java_target.write_bytes((STAGE/'WhatsAppUnderstandingEngine.java').read_bytes())
    BUILD.write_text(gradle,encoding='utf-8')
    print('PASS 3.9.5: contextual WhatsApp review proposals; independent tasks, topic-safe deduplication, explicit correction review')

if __name__=='__main__':apply()
