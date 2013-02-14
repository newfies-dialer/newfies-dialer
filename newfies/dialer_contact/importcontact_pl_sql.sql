DROP PROCEDURE IF EXISTS importcontact_pl_sql;

DELIMITER //

CREATE PROCEDURE `importcontact_pl_sql` (IN var_campaign_id INT(10), IN var_phonebook_id INT(10))
LANGUAGE SQL
BEGIN

    DECLARE no_more_rows BOOLEAN;
    DECLARE loop_cntr INT DEFAULT 0;
    DECLARE num_rows INT DEFAULT 0;
    DECLARE  prd_id INT(10);
    DECLARE  prd_contact VARCHAR(255);

    DECLARE  cur CURSOR FOR
        SELECT `id`, `contact` FROM `dialer_contact` WHERE phonebook_id=var_phonebook_id;

    -- Declare 'handlers' for exceptions
    DECLARE CONTINUE HANDLER FOR NOT FOUND
        SET no_more_rows = TRUE;

    /* for loggging information */
    DROP TABLE IF EXISTS infologs;
    CREATE  TABLE infologs (
        Id int(11) NOT NULL AUTO_INCREMENT,
        Msg varchar(255) NOT NULL,
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (Id)
    );


    OPEN cur;

    the_loop: LOOP

        FETCH cur INTO prd_id, prd_contact;

        -- break out of the loop if
          -- 1) there were no records, or
          -- 2) we've processed them all
        IF no_more_rows THEN
            CLOSE cur;
            LEAVE the_loop;
        END IF;

        INSERT INTO infologs (Msg) VALUES (CONCAT('Log Message : Insert contact id=',prd_id,' ; contact=',prd_contact,' ; var_campaign_id=',var_campaign_id,' ; var_phonebook_id=',var_phonebook_id));
        INSERT IGNORE INTO `dialer_subscriber` (`contact_id`, `campaign_id`, `duplicate_contact`, `status`, `created_date`, `updated_date`) VALUES (prd_id, var_campaign_id, prd_contact, 1, NOW(), NOW());

        -- the equivalent of a 'print statement' in a stored procedure
        -- it simply displays output for each loop
        select prd_id, prd_contact,var_campaign_id, var_phonebook_id;

        -- count the number of times looped
        SET loop_cntr = loop_cntr + 1;

    END LOOP the_loop;


END //
DELIMITER ;


