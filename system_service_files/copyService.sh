systemctl disable sanm
cp sanm.service /lib/systemd/system/sanm.service
chmod 644 /lib/systemd/system/sanm.service
systemctl enable sanm
systemctl restart sanm

systemctl disable webserver
cp webserver.service /lib/systemd/system/webserver.service
chmod 644 /lib/systemd/system/webserver.service
systemctl enable webserver
systemctl restart webserver

systemctl disable device_home_kasa
cp device_home_kasa.service /lib/systemd/system/device_home_kasa.service
chmod 644 /lib/systemd/system/device_home_kasa.service
systemctl enable device_home_kasa
systemctl restart device_home_kasa

systemctl disable device_home_weather
cp device_home_weather.service /lib/systemd/system/device_home_weather.service
chmod 644 /lib/systemd/system/device_home_weather.service
systemctl enable device_home_weather
systemctl restart device_home_weather

systemctl disable fauxmoToHomeCommanderServer
cp fauxmoToHomeCommanderServer.service /lib/systemd/system/fauxmoToHomeCommanderServer.service
chmod 644 /lib/systemd/system/fauxmoToHomeCommanderServer.service
systemctl enable fauxmoToHomeCommanderServer
systemctl restart fauxmoToHomeCommanderServer

systemctl disable fauxmo
cp fauxmo.service /lib/systemd/system/fauxmo.service
chmod 644 /lib/systemd/system/fauxmo.service
systemctl enable fauxmo
systemctl restart fauxmo