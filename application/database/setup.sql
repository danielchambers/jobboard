CREATE TABLE greenhouse_companies (
    id serial PRIMARY KEY,
    name VARCHAR(50) UNIQUE,
    timestamp_found TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true,
    jobs_available INT
);

CREATE TABLE lever_companies (
    id serial PRIMARY KEY,
    name VARCHAR(50) UNIQUE,
    timestamp_found TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true,
    jobs_available INT
);

CREATE TABLE myworkdayjobs_companies (
    id serial PRIMARY KEY,
    name VARCHAR(50) UNIQUE,
    region VARCHAR(5),
    uri VARCHAR(50),
    timestamp_found TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true,
    jobs_available INT
);