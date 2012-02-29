
#Run testing suit
cd newfies

#Run Full Test Suit
#./manage.py test --verbosity=2

#Run NewfiesApiTestCase
echo "manage.py test dialer_cdr.NewfiesTastypieApiTestCase --verbosity=2"
./manage.py test dialer_cdr.NewfiesTastypieApiTestCase --verbosity=2
echo ""
echo "Press any key to continue..."
read TEMP

#Run NewfiesAdminInterfaceTestCase
echo "manage.py test dialer_cdr.NewfiesAdminInterfaceTestCase --verbosity=2"
./manage.py test dialer_cdr.NewfiesAdminInterfaceTestCase --verbosity=2
echo ""
echo "Press any key to continue..."
read TEMP

#Run NewfiesCustomerInterfaceTestCase
echo "manage.py test dialer_cdr.NewfiesCustomerInterfaceTestCase --verbosity=2"
./manage.py test dialer_cdr.NewfiesCustomerInterfaceTestCase --verbosity=2
echo ""
echo "Press any key to continue..."
read TEMP

#Run NewfiesTastypieApiTestCase
echo "manage.py test dialer_cdr.NewfiesTastypieApiTestCase.test_create_campaign --verbosity=2"
./manage.py test dialer_cdr.NewfiesTastypieApiTestCase.test_create_campaign --verbosity=2
echo ""
echo "Press any key to continue..."
read TEMP

cd -

