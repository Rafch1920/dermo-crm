-- =====================================================
-- Dermo-CRM - Schéma Base de Données SQLite
-- =====================================================

-- Activation des foreign keys
PRAGMA foreign_keys = ON;

-- =====================================================
-- 1. UTILISATEURS
-- =====================================================
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE,
    full_name VARCHAR(100),
    role VARCHAR(20) DEFAULT 'trainer' CHECK (role IN ('admin', 'trainer', 'viewer')),
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT 1,
    last_login DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 2. RÉFÉRENTS COMMERCIAUX
-- =====================================================
CREATE TABLE referents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    zone VARCHAR(100),
    color VARCHAR(7) DEFAULT '#007bff', -- Couleur pour la carte
    target_pharmacies INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 3. PRODUITS
-- =====================================================
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200) NOT NULL,
    brand VARCHAR(100),
    category VARCHAR(100),
    description TEXT,
    argumentaire TEXT, -- Argumentaire commercial
    photo_path VARCHAR(255),
    documents JSON, -- Liste des documents attachés
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 4. CAMPAGNES
-- =====================================================
CREATE TABLE campaigns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    objectives TEXT,
    target_zones JSON, -- Zones ciblées
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('draft', 'active', 'paused', 'completed')),
    created_by INTEGER REFERENCES users(id),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 5. PHARMACIES / ENSEIGNES
-- =====================================================
CREATE TABLE pharmacies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200) NOT NULL,
    type VARCHAR(30) DEFAULT 'pharmacie' CHECK (type IN ('pharmacie', 'parapharmacie', 'grande_surface', 'autre')),
    address VARCHAR(255),
    city VARCHAR(100),
    postal_code VARCHAR(10),
    region VARCHAR(100),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    phone VARCHAR(20),
    email VARCHAR(100),
    referent_id INTEGER REFERENCES referents(id),
    is_active BOOLEAN DEFAULT 1,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 6. CONTACTS (par pharmacie)
-- =====================================================
CREATE TABLE contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pharmacy_id INTEGER NOT NULL REFERENCES pharmacies(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(50),
    phone VARCHAR(20),
    email VARCHAR(100),
    is_primary BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 7. AGENTS (par pharmacie)
-- =====================================================
CREATE TABLE agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pharmacy_id INTEGER NOT NULL REFERENCES pharmacies(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(50),
    phone VARCHAR(20),
    email VARCHAR(100),
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 8. VISITES
-- =====================================================
CREATE TABLE visits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pharmacy_id INTEGER NOT NULL REFERENCES pharmacies(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    visit_date DATETIME NOT NULL,
    duration INTEGER, -- Durée en minutes
    objective TEXT,
    notes TEXT,
    quality_score INTEGER CHECK (quality_score BETWEEN 1 AND 10),
    latitude DECIMAL(10, 8), -- GPS
    longitude DECIMAL(11, 8),
    is_completed BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 9. PIÈCES JOINTES
-- =====================================================
CREATE TABLE attachments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type VARCHAR(20) NOT NULL CHECK (entity_type IN ('visit', 'product', 'campaign', 'pharmacy')),
    entity_id INTEGER NOT NULL,
    filename VARCHAR(255) NOT NULL,
    original_name VARCHAR(255),
    file_type VARCHAR(50),
    file_size INTEGER,
    uploaded_by INTEGER REFERENCES users(id),
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 10. TABLES DE LIAISON (Many-to-Many)
-- =====================================================

-- Campagnes <-> Produits
CREATE TABLE campaign_products (
    campaign_id INTEGER REFERENCES campaigns(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    PRIMARY KEY (campaign_id, product_id)
);

-- Visites <-> Produits (produits formés)
CREATE TABLE visit_products (
    visit_id INTEGER REFERENCES visits(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    trained_agents_count INTEGER DEFAULT 0,
    notes TEXT,
    PRIMARY KEY (visit_id, product_id)
);

-- Pharmacies <-> Produits (disponibles)
CREATE TABLE pharmacy_products (
    pharmacy_id INTEGER REFERENCES pharmacies(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    is_available BOOLEAN DEFAULT 1,
    stock_status VARCHAR(20) DEFAULT 'normal',
    PRIMARY KEY (pharmacy_id, product_id)
);

-- Pharmacies <-> Campagnes (inscrites)
CREATE TABLE pharmacy_campaigns (
    pharmacy_id INTEGER REFERENCES pharmacies(id) ON DELETE CASCADE,
    campaign_id INTEGER REFERENCES campaigns(id) ON DELETE CASCADE,
    enrollment_date DATE DEFAULT CURRENT_DATE,
    status VARCHAR(20) DEFAULT 'active',
    PRIMARY KEY (pharmacy_id, campaign_id)
);

-- =====================================================
-- 11. LOGS D'ACTIVITÉ
-- =====================================================
CREATE TABLE activity_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(50) NOT NULL,
    entity_type VARCHAR(20),
    entity_id INTEGER,
    details JSON,
    ip_address VARCHAR(45),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- INDEXES POUR PERFORMANCE
-- =====================================================
CREATE INDEX idx_pharmacies_region ON pharmacies(region);
CREATE INDEX idx_pharmacies_referent ON pharmacies(referent_id);
CREATE INDEX idx_pharmacies_coords ON pharmacies(latitude, longitude);
CREATE INDEX idx_visits_pharmacy ON visits(pharmacy_id);
CREATE INDEX idx_visits_user ON visits(user_id);
CREATE INDEX idx_visits_date ON visits(visit_date);
CREATE INDEX idx_contacts_pharmacy ON contacts(pharmacy_id);
CREATE INDEX idx_agents_pharmacy ON agents(pharmacy_id);
CREATE INDEX idx_attachments_entity ON attachments(entity_type, entity_id);
CREATE INDEX idx_logs_user ON activity_logs(user_id);
CREATE INDEX idx_logs_created ON activity_logs(created_at);

-- =====================================================
-- DONNÉES INITIALES
-- =====================================================

-- Utilisateur admin par défaut (mot de passe: admin123)
-- Hash généré avec Werkzeug
INSERT INTO users (username, password_hash, email, full_name, role, is_active) VALUES 
('admin', 'scrypt:32768:8:1$...$...', 'admin@dermo-crm.local', 'Administrateur', 'admin', 1);

-- Quelques référents exemples
INSERT INTO referents (name, email, phone, zone, color) VALUES 
('Marie Dupont', 'marie.dupont@email.com', '06 12 34 56 78', 'Nord', '#e74c3c'),
('Jean Martin', 'jean.martin@email.com', '06 23 45 67 89', 'Sud', '#3498db'),
('Sophie Bernard', 'sophie.bernard@email.com', '06 34 56 78 90', 'Est', '#2ecc71');

-- Quelques produits exemples
INSERT INTO products (name, brand, category, description) VALUES 
('Crème Hydratante Ultra', 'Dermophil', 'Hydratation', 'Crème hydratante pour peaux sensibles'),
('Sérum Anti-Âge', 'SkinScience', 'Anti-Âge', 'Sérum concentré au rétinol'),
('Protection Solaire SPF50', 'SunCare', 'Protection', 'Écran solaire haute protection');

-- Campagne exemple
INSERT INTO campaigns (name, description, start_date, end_date, objectives, status) VALUES 
('Campagne Été 2024', 'Promotion des produits solaires', '2024-06-01', '2024-08-31', 'Former 100 pharmacies sur la gamme solaire', 'active');

-- Liaison campagne-produit
INSERT INTO campaign_products (campaign_id, product_id) VALUES (1, 3);
