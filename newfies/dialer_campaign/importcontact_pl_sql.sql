DROP PROCEDURE IF EXISTS importcontact_pl_sql;

CREATE PROCEDURE importcontact_pl_sql()
BEGIN

    DECLARE campaign_id INTEGER (10);
    DECLARE phonebook_id INTEGER (10);

    DECLARE cur1 CURSOR FOR
        SELECT id, campaign_id, contact FROM dialer_contact WHERE phonebook_id=phonebook_id;

    OPEN cur1;

    read_loop: LOOP
        FETCH cur1 INTO id, campaign_id, contact;

        INSERT INTO dialer_campaign_subscriber (contact_id, campaign_id, duplicate_contact, 1, NOW(), NOW()) VALUES (id, campaign_id, contact, status, created_date, updated_date)

    END LOOP;

    CLOSE cur1;

END;
