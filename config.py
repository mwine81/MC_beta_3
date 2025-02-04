from pathlib import Path
import plotly.express as px

MCCPDC_PRIMARY = '#12366c'
MCCPDC_SECONDARY = '#dcf2f9'
MCCPDC_ACCENT = '#f06842'

GROUP_DICT ={
    "Antihistamines/Nasal Agents/Cough & Cold/Respiratory/Misc (41-45)":'Respiratory',
    "Neuromuscular Agents (72-76)" :'Neuromuscular',
    "Gastrointestinal Agents (46-52)" :'Stomach/GI',
    "Anti-Infective Agents (01-16)": 'Anti-Infective',
    "Endocrine and Metabolic Agents (22-30)": 'Endocrine',
    "ADHD/Anti-Narcolepsy /Anti-Obesity/Anorexiant Agents (61-61)": 'Stimulants',
    "Nutritional Products (77-81)": 'Nutritional',
    "Central Nervous System Agents (57-60)": 'Central Nervous System',
    "Genitourinary Antispasmodics/Vaginal Products/Misc (53-56)": 'Genitourinary',
    "Hematological Agents (82-85)": 'Hematological',
    "Psychotherapeutic and Neurological Agents - Miscellaneous (62-63)": 'Parkinson/Neurological',
    "Miscellaneous Products (92-99)": 'Miscellaneous',
    "Dermatological/Anorectal/Mouth-Throat/Dental/Ophthalmic/Otic (86-91)": 'Dermatological/ENT',
    "Analgesic/Anti-Inflammatory/Migraine/Gout Agents/Anesthetics (64-71)": 'Pain/Inflammation',
    "Antineoplastic Agents and Adjunctive Therapies (21-21)": 'Cancer',
    "Cardiovascular Agents (31-40)": 'Cardiovascular',
}

DATA_DIR = Path("data")

COLOR_MAPPING = {k:v for k,v in zip(GROUP_DICT.values(),px.colors.qualitative.Light24_r[:len(GROUP_DICT.values())])}



