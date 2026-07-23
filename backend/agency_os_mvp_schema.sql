
-- =====================================================
-- Agency OS MVP PostgreSQL Schema
-- =====================================================

CREATE TYPE member_role AS ENUM (
  'OWNER',
  'MANAGER',
  'DESIGNER',
  'COPYWRITER',
  'VIDEO_EDITOR'
);

CREATE TYPE campaign_status AS ENUM (
  'PLANNING',
  'ACTIVE',
  'COMPLETED',
  'ARCHIVED'
);

CREATE TYPE task_status AS ENUM (
  'TODO',
  'ASSIGNED',
  'IN_PROGRESS',
  'READY_FOR_CLIENT',
  'CHANGES_REQUESTED',
  'APPROVED',
  'COMPLETED'
);

CREATE TYPE task_priority AS ENUM (
  'LOW',
  'MEDIUM',
  'HIGH',
  'URGENT'
);

CREATE TYPE approval_status AS ENUM (
  'PENDING',
  'APPROVED',
  'CHANGES_REQUESTED',
  'REJECTED'
);

CREATE TABLE users (
    id UUID PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    avatar_url TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE agencies (
    id UUID PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    owner_id UUID NOT NULL REFERENCES users(id),
    logo_url TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE agency_members (
    id UUID PRIMARY KEY,
    agency_id UUID NOT NULL REFERENCES agencies(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role member_role NOT NULL,
    joined_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(agency_id,user_id)
);

CREATE TABLE clients (
    id UUID PRIMARY KEY,
    agency_id UUID NOT NULL REFERENCES agencies(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    company_name VARCHAR(150) NOT NULL,
    contact_name VARCHAR(150),
    email VARCHAR(255),
    phone VARCHAR(30),
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE campaigns (
    id UUID PRIMARY KEY,
    agency_id UUID NOT NULL REFERENCES agencies(id) ON DELETE CASCADE,
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    name VARCHAR(150) NOT NULL,
    description TEXT,
    status campaign_status DEFAULT 'PLANNING',
    start_date DATE,
    end_date DATE,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE tasks (
    id UUID PRIMARY KEY,
    agency_id UUID NOT NULL REFERENCES agencies(id) ON DELETE CASCADE,
    campaign_id UUID REFERENCES campaigns(id) ON DELETE SET NULL,
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    created_by UUID NOT NULL REFERENCES users(id),
    assigned_to UUID REFERENCES users(id),
    status task_status DEFAULT 'TODO',
    priority task_priority DEFAULT 'MEDIUM',
    due_date TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE comments (
    id UUID PRIMARY KEY,
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id),
    message TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE attachments (
    id UUID PRIMARY KEY,
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    uploaded_by UUID NOT NULL REFERENCES users(id),
    file_name TEXT NOT NULL,
    file_url TEXT NOT NULL,
    mime_type VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE approvals (
    id UUID PRIMARY KEY,
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    status approval_status DEFAULT 'PENDING',
    comment TEXT,
    approved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE activity_logs (
    id UUID PRIMARY KEY,
    agency_id UUID NOT NULL REFERENCES agencies(id) ON DELETE CASCADE,
    task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_members_agency ON agency_members(agency_id);
CREATE INDEX idx_clients_agency ON clients(agency_id);
CREATE INDEX idx_campaigns_client ON campaigns(client_id);
CREATE INDEX idx_tasks_campaign ON tasks(campaign_id);
CREATE INDEX idx_tasks_assigned_to ON tasks(assigned_to);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_comments_task ON comments(task_id);
CREATE INDEX idx_attachments_task ON attachments(task_id);
CREATE INDEX idx_approvals_task ON approvals(task_id);
CREATE INDEX idx_activity_task ON activity_logs(task_id);
