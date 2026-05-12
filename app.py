import streamlit as st
import requests
import pandas as pd
import sqlite3
import os
import hashlib
from datetime import datetime

st.set_page_config(page_title="Scaleway Manager", page_icon="🚀", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 20px; border-bottom: 2px solid #f0f2f6; }
    .stTabs [data-baseweb="tab"] { height: 50px; font-weight: 600; font-size: 16px; color: #4F4F4F; }
    .stTabs [aria-selected="true"] { color: #007bff !important; border-bottom: 3px solid #007bff !important; }
    </style>
    """, unsafe_allow_html=True)

DB_PATH = "data/manager.db"
if not os.path.exists("data"): os.makedirs("data")

def db_query(query, params=(), fetch=False):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute(query, params)
        res = c.fetchall() if fetch else None
        conn.commit()
        return res
    except Exception as e:
        st.error(f"Erreur DB : {e}")
        return []
    finally:
        conn.close()

db_query("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, role TEXT, approved INTEGER DEFAULT 0)")
db_query("CREATE TABLE IF NOT EXISTS accounts (user_id INTEGER, name TEXT, access_key TEXT, secret_key TEXT, project_id TEXT, PRIMARY KEY(user_id, name))")
db_query("CREATE TABLE IF NOT EXISTS templates (user_id INTEGER, name TEXT, content TEXT, PRIMARY KEY(user_id, name))")

def make_hashes(password): return hashlib.sha256(str.encode(password)).hexdigest()
def check_hashes(password, hashed_text): return make_hashes(password) == hashed_text

if 'logged_in' not in st.session_state:
    if "session_token" in st.query_params:
        u_id = st.query_params["session_token"]
        res = db_query("SELECT id, username, role FROM users WHERE id=?", (u_id,), fetch=True)
        if res:
            st.session_state.update({'logged_in': True, 'user_id': res[0][0], 'username': res[0][1], 'role': res[0][2]})
    else:
        st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title("🔐 Accès Manager")
    t_login, t_reg = st.tabs(["Connexion", "Créer un compte"])
    with t_login:
        with st.form("login_form", clear_on_submit=False):
            u = st.text_input("Identifiant")
            p = st.text_input("Mot de passe", type='password')
            submit_login = st.form_submit_button("Se connecter", use_container_width=True)
            if submit_login:
                res = db_query("SELECT id, password, role, approved FROM users WHERE username=?", (u,), fetch=True)
                if res and check_hashes(p, res[0][1]):
                    if res[0][3] == 1 or res[0][2] == 'admin':
                        st.session_state.update({'logged_in': True, 'user_id': res[0][0], 'username': u, 'role': res[0][2]})
                        st.query_params["session_token"] = res[0][0]
                        st.rerun()
                    else: st.warning("Compte en attente d'approbation.")
                else: st.error("Identifiants incorrects.")
    with t_reg:
        with st.form("reg_form"):
            nu = st.text_input("Nouvel Identifiant")
            np = st.text_input("Nouveau Mot de passe", type='password')
            submit_reg = st.form_submit_button("Envoyer la demande", use_container_width=True)
            if submit_reg:
                count = db_query("SELECT COUNT(*) FROM users", fetch=True)[0][0]
                role, appr = ('admin', 1) if count == 0 else ('user', 0)
                db_query("INSERT INTO users (username, password, role, approved) VALUES (?,?,?,?)", (nu, make_hashes(np), role, appr))
                st.success("Demande enregistrée !")
    st.stop()

UID, ROLE = st.session_state['user_id'], st.session_state['role']
accounts_db = db_query("SELECT name, access_key, secret_key, project_id FROM accounts WHERE user_id=?", (UID,), fetch=True)
acc_names = [a[0] for a in accounts_db]
templates_db = db_query("SELECT name, content FROM templates WHERE user_id=?", (UID,), fetch=True)
tmpl_dict = {t[0]: t[1] for t in templates_db}

st.sidebar.subheader(f"👤 {st.session_state['username']}")
selected_acc = st.sidebar.selectbox("Profil Scaleway", ["---"] + acc_names)
SCW_SECRET, SCW_PROJECT = "", ""
if selected_acc != "---":
    curr = next(a for a in accounts_db if a[0] == selected_acc)
    SCW_SECRET, SCW_PROJECT = curr[2], curr[3]

if st.sidebar.button("🚪 Déconnexion"):
    st.session_state['logged_in'] = False
    st.query_params.clear()
    st.rerun()

HEADERS = {"X-Auth-Token": SCW_SECRET, "Content-Type": "application/json"}

tabs_labels = ["📊 Monitoring", "🌐 DNS", "🚀 Déploiement", "🌱 Écologie", "💰 Dépenses", "📝 Templates", "⚙️ Comptes"]
if ROLE == 'admin': tabs_labels.append("👑 Gouvernance")
tabs = st.tabs(tabs_labels)

with tabs[0]:
    if selected_acc == "---": st.info("Sélectionnez un profil.")
    else:
        for z in ["fr-par-1", "fr-par-2"]:
            r = requests.get(f"https://api.scaleway.com/instance/v1/zones/{z}/servers", headers=HEADERS)
            if r.status_code == 200:
                st.subheader(f"📍 Zone {z.upper()}")
                for s in r.json().get("servers", []):
                    c1, c2, c3, c4 = st.columns([3, 2, 1, 2])
                    c1.write(f"**{s['name']}**")
                    ip = s.get('public_ip',{}).get('address', 'N/A')
                    c2.code(ip)
                    c3.write("🟢" if s['state']=='running' else "🔴")
                    with c4:
                        b1, b2 = st.columns(2)
                        if b1.button("📸", key=f"sn_{s['id']}"):
                            requests.post(f"https://api.scaleway.com/instance/v1/zones/{z}/servers/{s['id']}/action", json={"action":"backup"}, headers=HEADERS)
                        if not s.get('protected', False) and b2.button("🗑️", key=f"tm_{s['id']}"):
                            requests.post(f"https://api.scaleway.com/instance/v1/zones/{z}/servers/{s['id']}/action", json={"action":"terminate"}, headers=HEADERS)
                            st.rerun()

with tabs[1]:
    st.header("Gestionnaire de Zones DNS")
    if selected_acc == "---": st.warning("Sélectionnez un profil.")
    else:
        z_res = requests.get("https://api.scaleway.com/domain/v2beta1/dns-zones?page_size=100", headers=HEADERS)
        if z_res.status_code == 200:
            zones = z_res.json().get("dns_zones", [])
            st.write(f"### Domaines disponibles ({len(zones)})")
            cols = st.columns(4)
            for i, z_item in enumerate(zones):
                if cols[i%4].button(f"🌍 {z_item['domain']}", key=f"zb_{z_item['domain']}", use_container_width=True):
                    st.session_state['active_domain'] = z_item['domain']
            domain = st.session_state.get('active_domain')
            if domain:
                st.divider()
                st.subheader(f"Records : {domain}")
                rec_res = requests.get(f"https://api.scaleway.com/domain/v2beta1/dns-zones/{domain}/records?page_size=100", headers=HEADERS)
                if rec_res.status_code == 200:
                    recs = rec_res.json().get("records", [])
                    st.dataframe(pd.DataFrame(recs)[['name','type','data','ttl']], use_container_width=True)
                    if st.button("📄 Générer Export BIND"):
                        bind = f"; Zone file for {domain}\n$ORIGIN {domain}.\n$TTL 3600\n\n"
                        for r in recs:
                            n = "@" if r['name'] == "" else r['name']
                            bind += f"{n.ljust(20)} {str(r['ttl']).ljust(8)} IN {r['type'].ljust(6)} {r['data']}\n"
                        st.code(bind, language="text")
                col_add, col_bulk = st.columns(2)
                with col_add:
                    st.markdown("### ➕ Ajouter un record")
                    with st.form("dns_add"):
                        n, t, v = st.text_input("Nom"), st.selectbox("Type", ["A","CNAME","TXT","MX"]), st.text_input("Valeur")
                        if st.form_submit_button("Ajouter"):
                            p = {"changes": [{"add": {"records": [{"name": n, "type": t, "data": v, "ttl": 3600}]}}]}
                            requests.patch(f"https://api.scaleway.com/domain/v2beta1/dns-zones/{domain}/records", json=p, headers=HEADERS)
                            st.rerun()
                with col_bulk:
                    st.markdown("### 📋 Importation en masse")
                    bulk = st.text_area("nom type valeur (un par ligne)", height=130)
                    if st.button("Lancer la synchronisation"):
                        new_recs = [{"name": l.split()[0], "type": l.split()[1], "data": l.split()[2], "ttl": 3600} for l in bulk.split('\n') if len(l.split()) >= 3]
                        requests.patch(f"https://api.scaleway.com/domain/v2beta1/dns-zones/{domain}/records", json={"changes": [{"set": {"records": new_recs}}]}, headers=HEADERS)
                        st.success("Zone synchronisée !")

with tabs[2]:
    if selected_acc != "---":
        st.header("Déployer une instance")
        with st.form("dep_v31"):
            dz, dn = st.radio("Zone", ["fr-par-1", "fr-par-2"], horizontal=True), st.text_input("Nom de la machine")
            dt_inst = st.selectbox("Type d'instance", ["PLAY2-PICO", "PLAY2-NANO", "PLAY2-MICRO", "DEV1-S", "DEV1-M"])
            dt_tmpl = st.selectbox("Template Docker Compose", list(tmpl_dict.keys()))
            if st.form_submit_button("Lancer le déploiement"):
                yml = tmpl_dict[dt_tmpl].replace("\n", "\n      ")
                payload = {"name": dn, "commercial_type": dt_inst, "image": "debian_bookworm", "project": SCW_PROJECT, "dynamic_ip_required": True}
                r = requests.post(f"https://api.scaleway.com/instance/v1/zones/{dz}/servers", json=payload, headers=HEADERS)
                if r.status_code == 201:
                    sid = r.json()['server']['id']
                    ci = f"#cloud-config\npackage_update: true\npackages: [docker.io, docker-compose-v2]\nwrite_files:\n  - path: /app/docker-compose.yml\n    content: |\n      {yml}\nruncmd:\n  - systemctl enable --now docker\n  - cd /app && docker compose up -d"
                    requests.patch(f"https://api.scaleway.com/instance/v1/zones/{dz}/servers/{sid}/user_data/cloud-init", data=ci, headers={"X-Auth-Token": SCW_SECRET, "Content-Type": "text/plain"})
                    requests.post(f"https://api.scaleway.com/instance/v1/zones/{dz}/servers/{sid}/action", json={"action": "poweron"}, headers=HEADERS)
                    st.success("Déploiement initié avec succès.")

with tabs[3]:
    st.header("🌱 Empreinte Environnementale")
    if selected_acc == "---": 
        st.info("Sélectionnez un profil.")
    else:
        env_type = st.radio("Type d'impact", ["Carbone", "Eau"], horizontal=True)
        r_org = requests.get("https://api.scaleway.com/account/v3/organizations", headers=HEADERS)
        if r_org.status_code == 200:
            organizations = r_org.json().get('organizations', [])
            if organizations:
                org_id = organizations[0].get('id')
                now = datetime.now()
                start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat() + "Z"
                end_date = now.isoformat() + "Z"
                metrics_url = "https://api.scaleway.com/environmental-impact/v1alpha1/usage/dashboard/metrics"
                params = {"organization_id": org_id, "start_date": start_date, "end_date": end_date}
                try:
                    r_metrics = requests.get(metrics_url, params=params, headers=HEADERS)
                    if r_metrics.status_code == 200:
                        data = r_metrics.json()
                        metrics = data.get("metrics", [])
                        if metrics:
                            df_metrics = pd.DataFrame(metrics)
                            search_term = 'carbon' if env_type == "Carbone" else 'water'
                            unit = "gCO2e" if env_type == "Carbone" else "ml"
                            df_filtered = df_metrics[df_metrics['metric_type'].str.contains(search_term, case=False)]
                            if not df_filtered.empty:
                                c1, c2 = st.columns(2)
                                total_val = df_filtered['value'].sum()
                                c1.metric(f"Total {env_type}", f"{total_val:.2f} {unit}")
                                c2.caption(f"Période : du {now.strftime('%d/%m/%Y')}")
                                st.subheader("Répartition par ressource")
                                chart_data = df_filtered.groupby('category')['value'].sum()
                                st.bar_chart(chart_data)
                                st.dataframe(df_filtered[['category', 'value', 'metric_type']], use_container_width=True, hide_index=True)
                                st.download_button("📥 Export CSV Empreinte", df_filtered.to_csv(index=False), "impact_environnemental.csv", "text/csv")
                            else: st.info(f"Aucune donnée de type {env_type} pour cette période.")
                        else: st.info("Aucune métrique retournée par Scaleway.")
                    else:
                        st.error(f"Erreur API ({r_metrics.status_code})")
                        st.json(r_metrics.json())
                except Exception as e: st.error(f"Erreur de connexion : {e}")

with tabs[4]:
    st.header("💰 Dépenses Mensuelles")
    if selected_acc == "---": st.info("Sélectionnez un profil.")
    else:
        r_bill = requests.get(f"https://api.scaleway.com/billing/v2beta1/invoices?project_id={SCW_PROJECT}", headers=HEADERS)
        if r_bill.status_code == 200:
            bill_data = r_bill.json().get("invoices", [])
            if bill_data:
                def format_price(price_obj):
                    if pd.isna(price_obj) or price_obj is None: return 0.0
                    units = price_obj.get('units', 0)
                    nanos = price_obj.get('nanos', 0)
                    return float(units) + (float(nanos) / 1000000000)
                df_bill = pd.DataFrame(bill_data)
                df_bill['Date'] = pd.to_datetime(df_bill['start_date']).dt.strftime('%m/%Y')
                df_bill['HT (€)'] = df_bill['total_untaxed'].apply(format_price)
                df_bill['TTC (€)'] = df_bill['total_taxed'].apply(format_price)
                df_bill['Statut'] = df_bill['state'].str.replace('paid', 'Payé').str.replace('voided', 'Annulé')
                st.dataframe(df_bill[['number', 'Date', 'HT (€)', 'TTC (€)', 'Statut']], use_container_width=True, hide_index=True)
                total_ttc = df_bill[df_bill['state'] == 'paid']['TTC (€)'].sum()
                st.info(f"**Total cumulé payé : {total_ttc:.2f} €**")
                st.download_button("📥 Export CSV Dépenses", df_bill.to_csv(index=False), "billing_details.csv", "text/csv")
            else: st.info("Aucune facture trouvée.")

with tabs[5]:
    st.header("Bibliothèque de Templates")
    with st.form("t_form"):
        tn, tc = st.text_input("Nom du template"), st.text_area("YAML Compose", height=200)
        if st.form_submit_button("Enregistrer"):
            db_query("INSERT OR REPLACE INTO templates VALUES (?,?,?)", (UID, tn, tc)); st.rerun()
    for t in templates_db:
        c1, c2 = st.columns([5,1])
        c1.write(f"📄 **{t[0]}**")
        if c2.button("Supprimer", key=f"t_{t[0]}"):
            db_query("DELETE FROM templates WHERE user_id=? AND name=?", (UID, t[0])); st.rerun()

with tabs[6]:
    st.header("Gestion des Profils")
    with st.form("acc_form"):
        an, ak, sk, pi = st.text_input("Nom"), st.text_input("Access Key"), st.text_input("Secret Key", type="password"), st.text_input("Project ID")
        if st.form_submit_button("Ajouter"):
            db_query("INSERT OR REPLACE INTO accounts VALUES (?,?,?,?,?)", (UID, an, ak, sk, pi)); st.rerun()
    for a in acc_names:
        c1, c2 = st.columns([5,1])
        c1.write(f"💼 **{a}**")
        if c2.button("Retirer", key=f"a_{a}"):
            db_query("DELETE FROM accounts WHERE user_id=? AND name=?", (UID, a)); st.rerun()

if ROLE == 'admin':
    with tabs[7]:
        st.header("Administration des accès")
        users = db_query("SELECT id, username, role, approved FROM users", fetch=True)
        for u_id, u_n, u_r, u_ap in users:
            if u_r == 'admin': continue
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.write(f"👤 **{u_n}** ({'Approuvé' if u_ap else 'En attente'})")
            if not u_ap and c2.button("✅ Approuver", key=f"ok_{u_id}"):
                db_query("UPDATE users SET approved=1 WHERE id=?", (u_id,)); st.rerun()
            if c3.button("🗑️ Supprimer", key=f"del_{u_id}"):
                db_query("DELETE FROM users WHERE id=?", (u_id,)); st.rerun()
