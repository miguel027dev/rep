import re
import unicodedata
from .workouts import movement

def _clean(v):
    return "".join(c for c in unicodedata.normalize("NFD", str(v or "")) if unicodedata.category(c)!="Mn").lower()

LIB = {
 "chest_machine": movement("Supino na máquina","Peitoral","Máquinas","Mantenha as escápulas apoiadas e controle a descida.",True),
 "db_bench": movement("Supino com halteres","Peitoral","Halteres","Controle a descida e mantenha os ombros estáveis.",True),
 "pushup": movement("Flexão inclinada","Peitoral","Peso corporal","Mantenha o corpo alinhado e ajuste a altura do apoio.",True),
 "row_cable": movement("Remada baixa","Costas","Cabos","Puxe com os cotovelos sem jogar o tronco para trás.",True),
 "row_db": movement("Remada unilateral","Costas","Halteres","Apoie-se com firmeza e mantenha a coluna neutra.",True),
 "row_bw": movement("Elevação de braços em W","Costas","Peso corporal","Deitado de barriga para baixo, mova os braços sem forçar a lombar."),
 "pulldown": movement("Puxada na polia","Costas","Cabos","Puxe em direção à parte alta do peito sem balanço.",True),
 "legpress": movement("Leg press","Pernas","Máquinas","Use amplitude confortável e mantenha a lombar apoiada.",True),
 "goblet": movement("Agachamento goblet","Pernas","Halteres","Mantenha os pés firmes e desça com controle.",True),
 "squat_bw": movement("Agachamento livre","Pernas","Peso corporal","Desça com controle em amplitude confortável.",True),
 "rdl": movement("Levantamento romeno","Posterior","Halteres","Leve o quadril para trás mantendo a coluna neutra.",True),
 "legcurl": movement("Mesa flexora","Posterior","Máquinas","Flexione os joelhos sem levantar o quadril."),
 "hipbridge": movement("Ponte de glúteos","Glúteos","Peso corporal","Eleve o quadril sem exagerar a curvatura lombar."),
 "shoulder_press": movement("Desenvolvimento na máquina","Ombros","Máquinas","Controle a descida e evite compensar com a lombar.",True),
 "db_press": movement("Desenvolvimento com halteres","Ombros","Halteres","Use amplitude confortável e tronco estável.",True),
 "wall_press": movement("Flexão na parede","Ombros","Peso corporal","Mantenha o corpo alinhado e use um ritmo controlado.",True),
 "lateral": movement("Elevação lateral","Ombros","Halteres","Eleve com controle sem usar impulso."),
 "curl": movement("Rosca com halteres","Bíceps","Halteres","Mantenha os cotovelos estáveis."),
 "triceps": movement("Tríceps na polia","Tríceps","Cabos","Estenda os cotovelos sem mover os ombros."),
 "calf": movement("Elevação de panturrilha","Panturrilha","Peso corporal","Suba e desça sem impulso e use apoio para equilíbrio."),
 "plank": movement("Prancha","Core","Peso corporal","Respire normalmente e pare antes de perder o alinhamento."),
}

def _has(p,e): return e=="Peso corporal" or e in (p.get("equipment") or [])
def _pick(p,*ids):
    for i in ids:
        if _has(p,LIB[i]["equipment"]): return LIB[i]
    return LIB[ids[-1]]
def _last(logs,name):
    for item in reversed(logs or []):
        sets=[s for s in item.get("setLogs",[]) if s.get("exerciseName")==name and s.get("completed")]
        if sets:return sets
    return []
def _prescribe(e,p,logs):
    minor=isinstance(p.get("age"),int) and p["age"]<18
    beginner=minor or p.get("experience")=="Iniciante";goal=p.get("goal") or "Criar uma rotina"
    sets=2 if beginner else (3 if goal=="Ganhar massa muscular" else 2)
    if e["group"] in (p.get("priorityMuscles") or []) and not minor: sets=min(4,sets+1)
    reps="20–40 s" if e["name"]=="Prancha" else (("6–10" if e.get("compound") else "10–15") if goal=="Ganhar massa muscular" else ("10–15" if goal=="Melhorar condicionamento" else "8–12"))
    rir=4 if minor else (3 if beginner else (2 if goal=="Ganhar massa muscular" else 3))
    rest=105 if goal=="Melhorar condicionamento" and e.get("compound") else (75 if goal=="Melhorar condicionamento" else (150 if e.get("compound") else 90))
    history=_last(logs,e["name"]);suggested=None;reason="Primeira referência: escolha uma carga confortável e registre suas repetições."
    if history and not minor:
        weighted=[s for s in history if float(s.get("weight") or 0)>0 and int(s.get("reps") or 0)>0]
        if weighted:
            last=max(float(s.get("weight") or 0) for s in weighted);hi=15 if "15" in reps else (12 if "12" in reps else 10)
            achieved=all(int(s.get("reps") or 0)>=hi and float(s.get("rir") or 0)>=rir for s in weighted)
            struggled=any(int(s.get("reps") or 0)<max(5,hi-4) or float(s.get("rir") or 0)<=0 for s in weighted)
            inc=1 if e["equipment"]=="Halteres" else 2.5
            suggested=round((last+inc if achieved else last*.975 if struggled else last)*2)/2
            reason="Você atingiu o topo da faixa com margem: pequeno aumento sugerido." if achieved else ("A última sessão ficou pesada: mantenha ou reduza levemente para recuperar qualidade." if struggled else "Mantenha a referência e tente melhorar reps ou controle antes de subir a carga.")
    return {**e,"sets":sets,"warmupSets":2 if e.get("compound") else 1,"reps":reps,"targetRir":rir,"restSeconds":rest,"suggestedLoad":suggested,"progressionReason":reason}

def _templates(p):
    chest=_pick(p,"chest_machine","db_bench","pushup");row=_pick(p,"row_cable","row_db","row_bw");pull=_pick(p,"pulldown","row_cable","row_db","row_bw");squat=_pick(p,"legpress","goblet","squat_bw");hinge=_pick(p,"rdl","hipbridge");press=_pick(p,"shoulder_press","db_press","wall_press");lat=_pick(p,"lateral","db_press","wall_press");ham=_pick(p,"legcurl","rdl","hipbridge");curl=_pick(p,"curl","plank");tri=_pick(p,"triceps","plank");calf=LIB["calf"];core=LIB["plank"]
    days=max(2,min(5,int(p.get("days") or 3)));minor=isinstance(p.get("age"),int) and p["age"]<18
    if minor or days==2:return [("Corpo inteiro A","Pernas · peito · costas",[squat,chest,row,hinge,core]),("Corpo inteiro B","Posterior · ombros · costas",[hinge,press,pull,squat,core]),("Corpo inteiro C","Pernas · peito · costas",[squat,chest,row,lat,core])][:(min(days,3) if minor else 2)]
    if days==3:return [("Corpo inteiro A","Peito · costas · pernas",[chest,row,squat,lat,core]),("Corpo inteiro B","Posterior · ombros · costas",[hinge,press,pull,tri,calf]),("Corpo inteiro C","Pernas · peito · braços",[squat,chest,row,curl,tri])]
    if days==4:return [("Superiores A","Peito · costas · ombros",[chest,row,press,lat,curl,tri]),("Inferiores A","Pernas · posterior · core",[squat,hinge,ham,calf,core]),("Superiores B","Costas · peito · braços",[pull,chest,row,lat,curl,tri]),("Inferiores B","Pernas · posterior · panturrilha",[squat,ham,hinge,calf,core])]
    return [("Superiores","Peito · costas · ombros",[chest,row,press,lat,curl]),("Inferiores","Pernas · posterior · core",[squat,hinge,ham,calf,core]),("Push","Peito · ombros · tríceps",[chest,press,lat,tri]),("Pull","Costas · bíceps",[pull,row,curl,core]),("Pernas","Quadríceps · posterior · panturrilha",[squat,ham,hinge,calf,core])]

def make_plan_v2(p=None,logs=None):
    p=p or {};logs=logs or [];minor=isinstance(p.get("age"),int) and p["age"]<18;restricted=bool(p.get("limitations")) and p.get("limitations")!="Nenhuma";minutes=max(25,min(75,int(p.get("sessionMinutes") or 50)));limit=4 if minutes<=35 else 5 if minutes<=50 else 6
    out=[]
    for idx,(name,focus,moves) in enumerate(_templates(p)):
        out.append({"id":idx,"name":name,"focus":focus,"kind":"strength","method":"REP V2 · técnica supervisionada" if minor else "REP V2 · Adaptive","minutes":minutes,"intensity":"3–4 repetições de reserva" if minor else ("2–3 repetições de reserva" if p.get("experience")=="Iniciante" else "1–3 repetições de reserva"),"recovery":"Distribua as sessões para recuperar os mesmos grupos musculares antes de treiná-los pesado novamente.","note":"A V2 mantém técnica, supervisão e progressão de carga com profissional como prioridade." if minor else ("Sua restrição continua ativa. O plano não substitui avaliação profissional." if restricted else "A V2 preserva exercícios por várias semanas e adapta volume/carga a partir do que você registra."),"progression":"Carga e progressão devem ser confirmadas com responsável e profissional." if minor else "O motor usa reps e RIR registrados para sugerir a próxima referência sem trocar exercícios aleatoriamente.","engine":"v2","exercises":[_prescribe(e,p,logs) for e in moves[:limit]]})
    return out

def select_workout_cards_v2(text,p,logs=None,next_workout_id=0):
    t=_clean(text)
    if not p.get("goal") or not p.get("experience") or not p.get("days") or not p.get("equipment"):return []
    if re.search(r"\b(dor|dores|lesao|lesoes|machucado|tontura)\b",t):return []
    if not (re.search(r"\b(treino|treinos|plano|rotina|ficha|exercicios)\b",t) and re.search(r"\b(qual|quero|mostre|mostra|monte|monta|ver|hoje|agora|meu|minha)\b",t)):return []
    plan=make_plan_v2(p,logs or []);letter=re.search(r"\btreino ([a-e])\b",t)
    if letter:return [plan[min(ord(letter.group(1))-97,len(plan)-1)]]
    if re.search(r"\b(hoje|agora|proximo|proxima)\b",t):return [plan[min(max(0,int(next_workout_id)),len(plan)-1)]]
    return plan

def workout_summary_v2(workouts,profile=None):
    profile=profile or {};first=str(profile.get("name") or "").split(" ")[0];prefix=(first+", ") if first and first!="Você" else ""
    if len(workouts)==1:
        w=workouts[0];return f"{prefix}o REP V2 separou {w['name'].lower()} para hoje. O card usa seu histórico recente para manter a progressão previsível.\n\nRegistre reps e RIR em cada série: é isso que alimenta a próxima recomendação."
    return f"{prefix}sua rotina V2 está nos {len(workouts)} cards abaixo. Ela mantém exercícios estáveis e adapta as próximas referências a partir das séries que você realmente registra."
