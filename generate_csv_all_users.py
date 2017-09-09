from app import models, db

f = open( 'PremiumAir_all_users.csv', 'w' )

users = models.User.query.all()

f.write("ID,First,Last,Email,Nickname,Username,Password Length,About Me,Last Seen,Admin\n")

for u in users:
    f.write( str(u.id) + "," + str(u.fname) + "," + str(u.lname) + "," + str(u.email) + "," + str(u.nickname) + "," + str(u.username) + "," + str(u.password_length) + "," + str(u.about_me) + "," + str(u.last_seen) + "," + str(u.admin) + "\n" )

f.close()
print "done"
