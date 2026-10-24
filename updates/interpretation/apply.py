#!/usr/bin/env python3
"""Integrate review-only multi-activity segmentation into existing WhatsApp proposal parser."""
from pathlib import Path
import shutil
src=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
shutil.copyfile("updates/interpretation/MultiActivityInterpreter.java",src/"MultiActivityInterpreter.java")
p=src/"MessageParser.java"
s=p.read_text(encoding="utf-8")
anchor='        String[] lines=bounded.split("(?:\\\\r?\\\\n)+|;\\\\s*");'
assert s.count(anchor)==1, "MessageParser.parse anchor changed"
s=s.replace(anchor,'''        // Each distinct activity is reviewed independently. Never create tasks automatically.
        List<MultiActivityInterpreter.Candidate> candidates=MultiActivityInterpreter.extract(bounded);
        if(!candidates.isEmpty()){
            for(MultiActivityInterpreter.Candidate candidate:candidates){
                Proposal item=parseOne(candidate.text,now,zone,manual);
                if(item.action||manual){
                    // Extracted candidate is evidence, not a verified deadline.
                    if(!item.dateKnown&&!candidate.dateHint.isEmpty()){
                        item.ambiguous=true;
                        item.reason="Fecha contextual: "+candidate.dateHint+". Confirma la fecha.";
                    }
                    out.add(item);
                }
                if(out.size()>=40)break;
            }
            if(!out.isEmpty())return out;
        }
''' +anchor,1)
p.write_text(s,encoding="utf-8")
print("PASS: MultiActivityInterpreter integrated into MessageParser.parse")
