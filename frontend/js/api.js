/** WuwaWebTool Frontend API Client — modified from XutheringWavesUID */
const API_BASE = window.API_BASE_URL || '';

// --- Auth helpers ---
function getStoredAuth() { const t=localStorage.getItem('wuwa_token'),d=localStorage.getItem('wuwa_did'),u=localStorage.getItem('wuwa_uid'),b=localStorage.getItem('wuwa_bat'); return {token:t,did:d,uid:u,bat:b}; }
function storeAuth(token,did,uid,bat){if(token)localStorage.setItem('wuwa_token',token);if(did)localStorage.setItem('wuwa_did',did);if(uid)localStorage.setItem('wuwa_uid',uid);if(bat)localStorage.setItem('wuwa_bat',bat);}
function clearAuth(){['wuwa_token','wuwa_did','wuwa_uid','wuwa_bat'].forEach(k=>localStorage.removeItem(k));}
function isLoggedIn(){const{token,did}=getStoredAuth();return!!(token&&did);}
function initFromUrlParams(){const p=new URLSearchParams(location.search),t=p.get('token'),d=p.get('did');if(t&&d){storeAuth(t,d);history.replaceState({},document.title,location.pathname);return true;}return false;}

// --- Cache helpers ---
const CP='wuwa_';
function cacheGet(k){try{const v=localStorage.getItem(CP+k);return v?JSON.parse(v):null;}catch(e){return null;}}
function cacheSet(k,v){localStorage.setItem(CP+k,JSON.stringify(v));}
function cacheClear(){const AUTH=['wuwa_token','wuwa_did','wuwa_uid','wuwa_bat'];Object.keys(localStorage).filter(k=>k.startsWith(CP)&&!AUTH.includes(k)).forEach(k=>localStorage.removeItem(k));}

// --- API calls ---
async function apiCall(endpoint, body) { const r=await fetch(API_BASE+endpoint,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}); if(!r.ok)throw new Error(`API ${r.status}`); return r.json(); }
function authBody(){const{uid,token,did,bat}=getStoredAuth();return{uid:uid||'',token:token||'',did:did||'',bat:bat||''};}
async function apiRefreshData(){return apiCall('/api/game/refresh',authBody());}
async function apiGetRoleList(){return apiCall('/api/game/role-list',authBody());}
async function apiGetRoleData(){return apiCall('/api/game/role-data',authBody());}
async function apiRefreshBat(){const{uid,token,did}=getStoredAuth();const r=await apiCall('/api/login/refresh-bat',{uid:uid||'',token,did});if(r.success)storeAuth(null,null,null,r.bat);return r;}

// --- Role detail with caching ---
async function apiGetRoleDetail(charId, forceRefresh) {
    const ck = 'roledetail_' + charId;
    if (!forceRefresh) { const cached = cacheGet(ck); if (cached) return cached; }
    const r = await apiCall('/api/game/role-detail/' + charId, authBody());
    if (r.success && r.data) cacheSet(ck, r);
    return r;
}

async function apiGetBaseData() { return apiCall('/api/game/base-data', authBody()); }
async function apiGetCalabash() { return apiCall('/api/game/calabash', authBody()); }
async function apiGetRoleDetailBatch(charIds) {
    const { uid, token, did, bat } = getStoredAuth();
    return apiCall('/api/game/role-detail-batch', { uid: uid || '', token: token || '', did: did || '', bat: bat || '', char_ids: charIds });
}

async function apiScoreCharacter(charId, roleData) {
    return apiCall('/api/score/character', { uid: getStoredAuth().uid, token: getStoredAuth().token, char_id: charId, role_data: roleData });
}
async function apiScoreBatch(charIds) {
    const { uid, token, did, bat } = getStoredAuth();
    return apiCall('/api/score/batch', { uid: uid || '', token: token || '', did: did || '', bat: bat || '', char_ids: charIds });
}

// --- Per-character score cache ---
function cacheGetScore(charId) { return cacheGet('score_' + charId); }
function cacheSetScore(charId, data) { cacheSet('score_' + charId, data); }

// --- Combined: load character detail + score with per-character caching ---
// Only calls official API on first load or when forceRefresh=true.
// Returns {detail, score} where detail is the raw role-detail data and score is the scoring result.
async function loadCharDetailAndScore(charId, forceRefresh) {
    if (!forceRefresh) {
        const cachedDetailResp = cacheGet('roledetail_' + charId);
        const cachedScore = cacheGetScore(charId);
        if (cachedDetailResp && cachedDetailResp.data && cachedScore) {
            return { detail: cachedDetailResp.data, score: cachedScore };
        }
    }

    // Fetch detail from official API (only when not cached or forceRefresh)
    const detailResp = await apiGetRoleDetail(charId, forceRefresh);
    if (!detailResp.success || !detailResp.data) {
        throw new Error(detailResp.msg || '获取角色详情失败');
    }

    // Score locally (no official API call — role_data is passed in request body)
    const scoreResp = await apiScoreCharacter(charId, detailResp.data);
    let scoreData = null;
    if (scoreResp.success && scoreResp.data) {
        scoreData = scoreResp.data;
        cacheSetScore(charId, scoreData);
    }

    return { detail: detailResp.data, score: scoreData };
}

// Hydrate a role list entry from per-character caches (detail + score).
// Mutates the entry in-place. Returns true if any cached data was applied.
function hydrateCharFromCache(entry) {
    const cid = String(entry.roleId || entry.role?.roleId || '');
    if (!cid) return false;
    let changed = false;

    // Hydrate detail
    const cachedDetailResp = cacheGet('roledetail_' + cid);
    if (cachedDetailResp && cachedDetailResp.data && !entry._detail) {
        entry._detail = cachedDetailResp.data;
        changed = true;
    }

    // Hydrate score
    const cachedScore = cacheGetScore(cid);
    if (cachedScore != null && entry._score == null) {
        entry._score = cachedScore.total_score || 0;
        entry._grade = getCompositeGrade(entry._score);
        changed = true;
    }

    return changed;
}

function getResourceUrl(type, filename) { return API_BASE + '/static/resource/' + type + '/' + filename; }
function getTextureUrl(sub, name) { return 'assets/textures/texture2d/' + sub + '/' + name; }

// Icon URL helpers
function getAttrIcon(attrName) { return getTextureUrl('attribute', 'attr_'+attrName+'.png'); }
function getWeaponTypeIcon(typeName) { return getTextureUrl('weapon_type', 'weapon_type_'+typeName+'.png'); }
function getAttrEffectIcon(name) { return getTextureUrl('attribute_effect', 'attr_'+name+'.png'); }

// Attribute name → element mapping for icons
const ATTR_ELEMENTS = ['冷凝','热熔','导电','气动','衍射','湮灭'];

// --- Constants ---
const ATTRIBUTES={1:{name:'冷凝',color:'#3598db'},2:{name:'热熔',color:'#ba372a'},3:{name:'导电',color:'#b96ad9'},4:{name:'气动',color:'#169179'},5:{name:'衍射',color:'#f1c40f'},6:{name:'湮灭',color:'#843fa1'}};
const WEAPON_TYPES={1:'长刃',2:'迅刀',3:'佩枪',4:'臂铠',5:'音感仪'};
const SKILL_ORDER=['常态攻击','共鸣技能','共鸣回路','共鸣解放','变奏技能','延奏技能','谐度破坏'];
const CHAIN_COLORS={0:'#95a5a6',1:'#34495e',2:'#3598db',3:'#169179',4:'#b96ad9',5:'#cc8c00',6:'#ba372a'};
const CHAIN_NAMES=['零链','一链','二链','三链','四链','五链','六链'];
const STANDARD_BANNER_NAMES=['维里奈','安可','凌阳','鉴心','卡卡罗'];

// Grade thresholds from .pyd total_grade: [0, 0.48, 0.6, 0.7, 0.78, 0.84] × 250
const GRADE_THRESHOLDS=[
    {min:210,label:'SSS',color:'#e63946'}, // red
    {min:195,label:'SS',color:'#f4a261'},  // orange
    {min:175,label:'S',color:'#e9c46a'},   // gold
    {min:150,label:'A',color:'#b96ad9'},   // purple
    {min:120,label:'B',color:'#457b9d'},   // blue
    {min:0,label:'C',color:'#6b8e6e'}      // green
];
function getCompositeGrade(score){for(const g of GRADE_THRESHOLDS)if(score>=g.min)return g;return GRADE_THRESHOLDS[GRADE_THRESHOLDS.length-1];}

// Per-echo grade: 0-50 scale (from score.py)
const ECHO_GRADES=[
    {min:41.7,label:'SSS',color:'#e63946'},
    {min:38.3,label:'SS',color:'#f4a261'},
    {min:35,label:'S',color:'#e9c46a'},
    {min:30,label:'A',color:'#b96ad9'},
    {min:24,label:'B',color:'#457b9d'},
    {min:0,label:'C',color:'#6b8e6e'}
];
function getEchoGrade(score){for(const g of ECHO_GRADES)if(score>=g.min)return g;return ECHO_GRADES[ECHO_GRADES.length-1];}

// Substat max values (from game data)
const SUBSTAT_MAX={ '暴击':10.5,'暴击伤害':21.0,'攻击%':11.6,'生命%':11.6,'防御%':15.0,'共鸣效率':12.4,'普攻伤害加成':11.6,'重击伤害加成':11.6,'共鸣技能伤害加成':11.6,'共鸣解放伤害加成':11.6,'治疗效果加成':11.6 };
const SUBSTAT_MIN={ '暴击':6.3,'暴击伤害':12.6,'攻击%':6.4,'生命%':6.4,'防御%':8.2,'共鸣效率':6.8,'普攻伤害加成':6.4,'重击伤害加成':6.4,'共鸣技能伤害加成':6.4,'共鸣解放伤害加成':6.4,'治疗效果加成':6.4 };

// Weight-to-color: higher weight = brighter color
function weightColor(weight) {
    if (weight == null) return '#888';
    if (weight >= 0.8) return '#ff6347'; // red - core stat
    if (weight >= 0.5) return '#ffd700'; // gold - important
    if (weight >= 0.3) return '#c0c0c0'; // silver - decent
    if (weight >= 0.1) return '#888';    // grey - marginal
    return '#555';                        // dim - useless
}

function substatQuality(name, valueStr) {
    const v = parseFloat(valueStr) || 0;
    const max = SUBSTAT_MAX[name];
    if (!max) return { tier: 'mid', color: '#c0c0c0' };
    const min = SUBSTAT_MIN[name] || max * 0.6;
    const pct = (v - min) / (max - min);
    // >= 90% max → red (god roll)
    if (pct >= 0.9) return { tier: 'sss', color: '#ff4500' };
    // >= 70% max → gold (great)
    if (pct >= 0.7) return { tier: 's', color: '#e9c46a' };
    // >= 45% max → purple (good)
    if (pct >= 0.45) return { tier: 'a', color: '#b96ad9' };
    // >= 20% max → blue (ok)
    if (pct >= 0.2) return { tier: 'b', color: '#457b9d' };
    // < 20% max → green/grey (low)
    return { tier: 'c', color: '#6b8e6e' };
}
