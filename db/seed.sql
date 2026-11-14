INSERT INTO public.companhia_aerea (companhia, cidade) VALUES
    ('latam', 'sjc'), ('latam', 'bel'), ('gol', 'bel'), ('azul', 'campinas')
ON CONFLICT DO NOTHING;

INSERT INTO public.cidades (cidade, turno) VALUES
    ('sjc', 'tarde'), ('sjc', 'noite'), ('bel', 'manha'), ('campinas', 'noite')
ON CONFLICT DO NOTHING;
