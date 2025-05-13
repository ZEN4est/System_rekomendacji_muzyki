CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE OR REPLACE FUNCTION validate_user_insert()
RETURNS TRIGGER AS $$
BEGIN
    -- Sprawdzenie poprawności formatu e-maila
    IF NEW.email !~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$' THEN
        RAISE EXCEPTION 'Niepoprawny format adresu e-mail: %', NEW.email;
    END IF;

    -- Sprawdzenie unikalności e-maila (jeśli nawet UNIQUE istnieje, tu można rzucić własny komunikat)
    IF EXISTS (SELECT 1 FROM users WHERE email = NEW.email) THEN
        RAISE EXCEPTION 'Użytkownik z adresem e-mail % już istnieje.', NEW.email;
    END IF;

    -- Sprawdzenie unikalności username
    IF EXISTS (SELECT 1 FROM users WHERE username = NEW.username) THEN
        RAISE EXCEPTION 'Nazwa użytkownika % jest już zajęta.', NEW.username;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER trg_validate_user_insert
BEFORE INSERT ON users
FOR EACH ROW
EXECUTE FUNCTION validate_user_insert();


