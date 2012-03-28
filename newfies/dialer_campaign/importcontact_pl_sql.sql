
DROP PROCEDURE IF EXISTS importcontact_pl_sql;


DELIMITER //

CREATE PROCEDURE `importcontact_pl_sql` (IN campaign_id INT(10), IN phonebook_id INT(10))
LANGUAGE SQL  
BEGIN

    DECLARE cur CURSOR FOR SELECT `id`, `contact` FROM `dialer_contact` WHERE phonebook_id=phonebook_id;

    OPEN cur;
    read_loop: LOOP
        FETCH cur INTO campaign_id;

        INSERT INTO `dialer_campaign_subscriber` (`contact_id`, `campaign_id`, `duplicate_contact`, `status`, `created_date`, `updated_date`) VALUES (id, campaign_id, contact, 1, NOW(), NOW());

    END LOOP;
    CLOSE cur;

END //
DELIMITER ;
