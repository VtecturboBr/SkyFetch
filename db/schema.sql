CREATE TABLE IF NOT EXISTS public.companhia_aerea (
    companhia TEXT NOT NULL CHECK (length(trim(companhia)) > 0),
    cidade TEXT NOT NULL CHECK (length(trim(cidade)) > 0),
    PRIMARY KEY (companhia, cidade)
);

CREATE TABLE IF NOT EXISTS public.cidades (
    cidade TEXT NOT NULL CHECK (length(trim(cidade)) > 0),
    turno TEXT NOT NULL CHECK (turno IN ('manha', 'tarde', 'noite')),
    PRIMARY KEY (cidade, turno)
);
