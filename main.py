from flask import Flask, render_template, request, redirect, session, make_response
import matplotlib
import matplotlib.pyplot as plt
import numpy
import pandas
import json
import pyodbc
import datetime
matplotlib.use("Agg")

app = Flask(__name__)
app.secret_key = 'secret_key'

# create a connection with the pyodbc using the needed credentials
connecting = pyodbc.connect(
    "Driver={SQL Server Native Client 11.0};"
    "Server=YURRRRRCHIK\EUROVISIONSERVER;"
    "Database=EVinYourVisionDB;"
    "Trusted_Connection=yes;")
# create an instance and execute using the select command to retrieve your table details
# loop through the result to obtain your table data


class CurrentUser:
    _current_username = ""
    _current_access = ""
    _current_password = ""

    def set_username(self, username):
        self._current_username = username

    def set_access(self, access):
        self._current_access = access

    def set_password(self, password):
        self._current_password = password

    def get_username(self):
        return self._current_username

    def get_access(self):
        return self._current_access

    def get_password(self):
        return self._current_password

    def anonim(self):
        if self.get_username() == "":
            return True

    def admin(self):
        if self.get_access() == '(True,)':
            return True

    def leave(self):
        self._current_username = ""
        self._current_access = ""
        self._current_password = ""


class Authorization:
    _login = ""
    _password = ""
    _right_password = None
    _logins = []
    _passwords = []
    symbols = '  0 1 2 3 4 - a b c d e f g h i j k l m n o p q r s t u v w x y z A B C D E F G H I J K L M N O P Q R S T U V W X Y Z 5 6 7 8 9  '
    symbols = symbols.split(" ")

    def __init__(self, entered_login, entered_password):
        self._login = entered_login
        self._password = entered_password

    def get_right_password(self):
        return self._right_password

    def set_right_password(self, password):
        self._right_password = password

    def add_login(self, log):
        self._logins.append(log)

    def get_logins(self):
        return self._logins

    def get_passwords(self):
        return self._passwords

    def crypt(self):
        encrypted = []
        n = len(self.symbols)
        for i in self._right_password:
            for j in range(n - 1):
                if i == self.symbols[j]:
                    encrypted.append(self.symbols[n - j - 1])
        encrypted = "".join(encrypted)
        return encrypted

    def add_password(self, password):
        self._passwords.append(password)


class Registration(Authorization):
    _age = None
    _zodiac_sign = ""
    _country = ""
    _gender = ""

    def __init__(self, entered_login, entered_password, entered_age, entered_zodiac, entered_gender, entered_country):
        super(Registration, self).__init__(entered_login, entered_password)
        _age = entered_age
        _zodiac_sign = entered_zodiac
        _country = entered_country
        _gender = entered_gender

    def add_password(self, password):
        self._passwords.append(password)

    def crypt(self):
        encrypted = []
        n = len(self.symbols)
        for i in self._password:
            for j in range(n - 1):
                if i == self.symbols[j]:
                    encrypted.append(self.symbols[n - j - 1])
        encrypted = "".join(encrypted)
        return encrypted


class NewEdition:
    def __init__(self, year, host_city, host_country, venue, slogan, to_rank,
                 n_of_countries, n_of_sf1_countries, n_of_sf2_countries, n_of_f_countries):
        self.countries = {}
        self.artists = {}
        self.songs = {}
        self.songwriters = {}
        self.authors = {}
        self.broadcasters = {}
        self.sf = {}
        self.sf_place = {}
        self.sf_points = {}
        self.f_place = {}
        self.f_points = {}
        self.year = year
        self.host_city = host_city
        self.host_country = host_country
        self.venue = venue
        self.slogan = slogan
        self.to_rank = to_rank
        self.n_of_countries = n_of_countries
        self.n_of_sf1_countries = n_of_sf1_countries
        self.n_of_sf2_countries = n_of_sf2_countries
        self.n_of_f_countries = n_of_f_countries

    def year_is_not_valid(self):
        if self.year == "" or int(self.year) < 1956 or int(self.year) > int(datetime.date.today().year) + 1:
            return True
        else:
            return False

    def not_matching_number_of_countries(self):
        if self.n_of_countries == "" and self.countries.__len__() != 0:
            return True
        if self.countries.__len__() != int(self.n_of_countries):
            print(self.countries.__len__())
            print(int(self.n_of_countries))
            return True
        if self.n_of_sf1_countries != "" and self.n_of_sf2_countries != "" and self.n_of_f_countries != "":
            if (int(self.n_of_f_countries) - 20 + int(self.n_of_sf1_countries) + int(self.n_of_sf2_countries)
                    != int(self.n_of_countries)):
                return True
        else:
            return False


class Edition:
    def __init__(self, year, host_city, host_country, venue, slogan, to_rank):
        self.year = year
        self.host_city = host_city
        self.host_country = host_country
        self.venue = venue
        self.slogan = slogan
        self.to_rank = to_rank

    def year_is_not_valid(self):
        if self.year == "" or int(self.year) < 1956 or int(self.year) > int(datetime.date.today().year) + 30:
            return True
        else:
            return False


class NumberOfEntries:
    def __init__(self, n_of_sf1_countries, n_of_sf2_countries, n_of_f_countries, n_of_countries):
        self.n_of_countries = n_of_countries
        self.n_of_sf1_countries = n_of_sf1_countries
        self.n_of_sf2_countries = n_of_sf2_countries
        self.n_of_f_countries = n_of_f_countries


current_user = CurrentUser()


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        authorization = Authorization(username, password)
        login_cursor = connecting.cursor()
        login_cursor.execute('SELECT Login FROM Users')
        for curs in login_cursor:
            curs = str(curs)
            authorization.add_login(curs)
        login_cursor.close()
        password_cursor = connecting.cursor()
        password_cursor.execute("SELECT Password FROM Users where Login = '" + username + "'")
        for curs in password_cursor:
            authorization.set_right_password(str(curs))
        password_cursor.close()
        if authorization.get_right_password() is None:
            return render_template('login.html', error_message='Invalid credentials')
        decrypted_password = authorization.crypt()
        access_cursor = connecting.cursor()
        access_cursor.execute("SELECT access FROM Users where Login = '" + username + "'")
        access = None
        for curs in access_cursor:
            access = str(curs)
        access_cursor.close()
        username = f"('{username}',)"
        if username in authorization.get_logins() and password == decrypted_password and access == '(False,)':
            session['logged_in'] = True
            current_user.set_access(access)
            username = request.form['username']
            current_user.set_username(username)
            current_user.set_password(password)
            return redirect('/home')
        elif username in authorization.get_logins() and password == decrypted_password and access == '(True,)':
            session['logged_in'] = True
            current_user.set_access(access)
            username = request.form['username']
            current_user.set_username(username)
            current_user.set_password(password)
            return redirect('/admin')
        else:
            return render_template('login.html', error_message='Invalid credentials')
    return render_template('login.html')


@app.route('/registration', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        age = request.form['age']
        if age == "":
            age = '-1'
        age = int(age)
        if age <= 6:
            age = -1
        zodiac_sign = request.form['Zodiac Sign']
        gender = request.form['Gender']
        country = request.form['Country']
        registration = Registration(username, password, age, zodiac_sign, gender, country)
        for i in username:
            if i not in registration.symbols:
                return render_template('registration.html',
                                       error_message="Username can't contain '" + i + "' symbol")
        for i in password:
            if i not in registration.symbols:
                return render_template('registration.html',
                                       error_message="Password can't contain '" + i + "' symbol")
        login_cursor = connecting.cursor()
        login_cursor.execute('SELECT Login FROM Users')
        for curs in login_cursor:
            curs = str(curs)
            registration.add_login(curs)
        login_cursor.close()
        if f"('{username}',)" in registration.get_logins():
            return render_template('registration.html',
                                   error_message='User with this username already exists')
        if len(password) != 8:
            return render_template('registration.html',
                                   error_message="Password should contain 8 symbols!")
        encrypted_password = registration.crypt()
        password_cursor = connecting.cursor()
        password_cursor.execute('SELECT Password FROM Users')
        for curs in password_cursor:
            curs = str(curs)
            registration.add_password(curs)
        password_cursor.close()
        if f"('{encrypted_password}',)" in registration.get_passwords():
            return render_template('registration.html',
                                   error_message='User with this password already exists')
        elif (f"('{username}',)" not in registration.get_logins()
              and f"('{encrypted_password}',)" not in registration.get_passwords()):
            registration_cursor = connecting.cursor()
            registration_cursor.execute(f"insert into users (Login, Password, Age, ZodiacSign, Gender, Country) "
                                        f"values ('{username}', '{encrypted_password}', {age}, "
                                        f"'{zodiac_sign}', '{gender}', '{country}')")
            registration_cursor.close()
            connecting.commit()
            access = '(False,)'
            current_user.set_username(username)
            current_user.set_access(access)
            current_user.set_password(encrypted_password)
            return redirect('/home')
    return render_template('registration.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    current_user.leave()
    return redirect('/')


@app.errorhandler(404)
@app.errorhandler(500)
def page_not_found():
    return render_template('404.html', access=current_user.get_access()), 404


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if current_user.anonim():
        return render_template("404.html")
    if not current_user.admin():
        return render_template("404.html", access=current_user.get_access())
    users_cursor = connecting.cursor()
    users_cursor.execute('SELECT Login, ZodiacSign, Gender, Country, Age, Access FROM Users')
    users_cursor = users_cursor.fetchall()
    users = []
    for curs in users_cursor:
        user = []
        for i in range(6):
            user.append(curs[i])
        users.append(user)
    if request.method == "POST":
        df = pandas.DataFrame(users[0:],
                              columns=["Login", "Zodiac Sign", "Gender", "Country", "Age", "Access"])
        excel_file = 'static/users.xlsx'
        df.to_excel(excel_file, index=False)
        # Create a response with the Excel file
        response = make_response()
        response.headers['Content-Disposition'] = 'attachment; filename=users.xlsx'
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Cache-Control'] = 'no-cache'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        response.headers['Content-Transfer-Encoding'] = 'binary'
        response.data = open(excel_file, 'rb').read()
    n_users = users_cursor.__len__()
    admins_cursor = connecting.cursor()
    admins_cursor.execute("SELECT * FROM Users where Access = 1")
    admins_cursor = admins_cursor.fetchall()
    n_admins = admins_cursor.__len__()
    rankings_cursor = connecting.cursor()
    rankings_cursor.execute('SELECT * from rankings')
    rankings_cursor = rankings_cursor.fetchall()
    n_rankings = rankings_cursor.__len__()
    active_user_cursor = connecting.cursor()
    active_user_cursor.execute('select Login, count(rankings.UserID) from rankings '
                               'left join users on users.UserID = rankings.UserID '
                               'group by Login order by count(rankings.UserID) desc')
    active_user_cursor = active_user_cursor.fetchone()
    users_countries_cursor = connecting.cursor()
    users_countries_cursor.execute('select Country, count(Country) from users group by Country')
    users_countries = users_countries_cursor.fetchall()
    users_countries_dict = {}
    for curs in users_countries:
        for i in range(2):
            users_countries_dict[curs[0]] = float(curs[1])
    countries_labels = []
    for key in users_countries_dict.keys():
        countries_labels.append(key)
    countries_values = []
    for value in users_countries_dict.values():
        countries_values.append(value)
    countries_values = numpy.array(countries_values)
    plt.pie(countries_values, labels=countries_labels, autopct='%1.1f%%', textprops={'size': 'smaller'})
    plot_countries = 'static/users_countries.png'
    plt.savefig(plot_countries)
    plt.clf()
    # plt.close()
    return render_template("admin.html", cursor=users_cursor, N_users=n_users, N_admins=n_admins,
                           N_rankings=n_rankings, active_user=active_user_cursor, plot_countries=plot_countries,
                           user=current_user.get_username())


@app.route('/<user>', methods=['GET', 'POST'])
def change_rights(user):
    if current_user.anonim():
        return render_template("404.html")
    if not current_user.admin():
        return render_template("404.html", access=current_user.get_access())
    cursor = connecting.cursor()
    cursor.execute("UPDATE users SET access = "
                   "CASE WHEN access = 1 THEN 0 "
                   "WHEN access = 0 THEN 1 "
                   "ELSE access END "
                   "where Login = '" + user + "'")
    cursor.close()
    connecting.commit()
    return redirect('/admin')


@app.route('/home', methods=['GET', 'POST'])
def home():
    if current_user.anonim():
        return render_template("404.html")
    editions_cursor = connecting.cursor()
    editions_cursor.execute("select Editions.Year, HostCity, HostCountry, Venue, Slogan, Country, Song, Artist, Total "
                            "from editions left join NumbersOfEntries "
                            "on editions.EditionID = NumbersOfEntries.EditionID "
                            "left join WinnerEdition on WinnerEdition.EditionID = editions.EditionID "
                            "left join Winners on WinnerEdition.WinnerID = winners.WinnerID ")
    editions = editions_cursor.fetchall()
    editions_to_rank_cursor = connecting.cursor()
    editions_to_rank_cursor.execute("select Editions.Year, HostCity, HostCountry "
                                    "from editions left join NumbersOfEntries "
                                    "on editions.EditionID = NumbersOfEntries.EditionID where toRank = 1 ")
    editions_to_rank = editions_to_rank_cursor.fetchall()
    select_query = ("select distinct Editions.Year, HostCity, HostCountry, Venue, "
                    "Slogan, Winners.Country, Winners.Song, Winners.Artist, Total from editions "
                    "left join NumbersOfEntries on editions.EditionID = NumbersOfEntries.EditionID "
                    "left join WinnerEdition on WinnerEdition.EditionID = editions.EditionID "
                    "left join Winners on WinnerEdition.WinnerID = winners.WinnerID "
                    "left join EntryEdition on Editions.EditionID = EntryEdition.EditionID "
                    "left join Entries on Entries.EntryID = EntryEdition.EntryID "
                    "left join CountryEntry on CountryEntry.EntryID = Entries.EntryID "
                    "left join Country on Country.CountryID = CountryEntry.CountryID "
                    "left join SongEntry on Entries.EntryID = SongEntry.EntryID "
                    "left join Song on Song.SongID = SongEntry.SongID "
                    "left join SongArtist on SongArtist.SongID = Song.SongID "
                    "left join Artist on SongArtist.ArtistID = Artist.ArtistID "
                    "left join BroadcasterEntry on Entries.EntryID = BroadcasterEntry.EntryID "
                    "left join Broadcaster on BroadcasterEntry.BroadcasterID = Broadcaster.BroadcasterID ")
    if request.method == "POST":
        search = request.form['search']
        filtr = request.form['filter']
        if filtr == "Year" and search != "":
            adding = (" where Editions.Year LIKE '%" + search + "%'")
        elif filtr == "Winner" and search != "":
            adding = (" where Winners.Country LIKE '%" + search + "%' or Winners.Song LIKE '%" + search +
                      "%' or Winners.Artist LIKE '%" + search + "%'")
        elif filtr == "Country" and search != "":
            adding = (" where Entries.Country LIKE '%" + search + "%'")
        elif filtr == "Host" and search != "":
            adding = (" where HostCity LIKE '%" + search + "%' or HostCountry LIKE '%" + search +
                      "%' or Venue LIKE '%" + search + "%' or Slogan LIKE '%" + search + "%'")
        elif filtr == "Song" and search != "":
            adding = (" where Song.Name LIKE '%" + search + "%'")
        elif filtr == "Artist" and search != "":
            adding = (" where Artist.Name LIKE '%" + search + "%'")
        elif filtr == "Broadcaster" and search != "":
            adding = (" where Broadcaster.Name LIKE '%" + search + "%'")
        elif filtr == "Authors" and search != "":
            adding = (" where Song.Songwriter LIKE '%" + search + "%' or Song.Author LIKE '%" + search + "%'")
        else:
            adding = ""
        print(select_query + adding)
        editions_cursor.execute(select_query + adding)
        editions = editions_cursor.fetchall()
        if editions.__len__() == 0:
            search_message = "No results found"
            return render_template("main.html", cursor=editions,
                                   cursor1=editions_to_rank, access=current_user.get_access(), search=search,
                                   search_message=search_message)
        return render_template("main.html", cursor=editions,
                               cursor1=editions_to_rank, access=current_user.get_access(), search=search)
    return render_template("main.html", cursor=editions,
                           cursor1=editions_to_rank, access=current_user.get_access())


@app.route('/add_edition', methods=["GET", "POST"])
def add_edition():
    if current_user.anonim():
        return render_template("404.html")
    if not current_user.admin():
        return render_template("404.html", access=current_user.get_access())
    current_cursor = []
    all_countries_cursor = connecting.cursor()
    all_countries_cursor.execute('select name from Country order by Name')
    for curs in all_countries_cursor:
        for i in range(1):
            current_cursor.append(curs[i])
    if request.method == "POST":
        year = request.form['Year']
        host_city = request.form['HostCity']
        host_country = request.form['HostCountry']
        venue = request.form['Venue']
        slogan = request.form['Slogan']
        to_rank = request.form['toRank']
        num_of_countries = request.form['Number of participants']
        num_of_sf1_countries = request.form['Number of participants in SF1']
        num_of_sf2_countries = request.form['Number of participants in SF2']
        num_of_f_countries = request.form['Number of participants in final']
        new_edition = NewEdition(year, host_city, host_country, venue, slogan, to_rank,
                                 num_of_countries, num_of_sf1_countries, num_of_sf2_countries, num_of_f_countries)
        new_edition.countries = request.form.getlist('participating_countries[]')
        if new_edition.year_is_not_valid():
            error_message = "Invalid year"
            return render_template("add_edition.html", access=current_user.get_access(),
                                   error_message=error_message, current_cursor=current_cursor)
        if "Other" in new_edition.countries:
            new_edition.countries.remove("Other")
            missing_participants = request.form.getlist('MissingCountry')
            for participant in missing_participants:
                if participant != "":
                    if participant[0] == " ":
                        error_message = "Invalid country"
                        return render_template("add_edition.html", access=current_user.get_access(),
                                               error_message=error_message, current_cursor=current_cursor)
                    new_edition.countries.append(participant)
                    if participant not in current_cursor:
                        countries_cursor = connecting.cursor()
                        countries_cursor.execute(f"insert into country (name, DebutYear) values "
                                                 f"('{participant}', {new_edition.year})")
                        countries_cursor.commit()
        for participant in new_edition.countries:
            new_edition.artists[participant] = request.form[participant + 'artist']
            new_edition.songs[participant] = request.form[participant + 'song']
            new_edition.songwriters[participant] = request.form[participant + 'songwriter']
            new_edition.authors[participant] = request.form[participant + 'author']
            new_edition.broadcasters[participant] = request.form[participant + 'broadcaster']
            new_edition.sf[participant] = request.form[participant + 'SF']
            new_edition.sf_place[participant] = request.form[participant + 'SFPlace']
            new_edition.sf_points[participant] = request.form[participant + 'SFPoints']
            new_edition.f_place[participant] = request.form[participant + 'FPlace']
            new_edition.f_points[participant] = request.form[participant + 'FPoints']
        if new_edition.not_matching_number_of_countries():
            error_message = "Entered numbers of countries doesn't match with number of selected countries"
            return render_template("add_edition.html", access=current_user.get_access(),
                                   error_message=error_message, current_cursor=current_cursor)
        new_edition_cursor = connecting.cursor()
        new_edition_cursor.execute(f"insert into editions (Year, HostCity, HostCountry, Venue, Slogan, toRank) "
                                   f"values ({new_edition.year}, '{new_edition.host_city}', "
                                   f"'{new_edition.host_country}', '{new_edition.venue}', "
                                   f"'{new_edition.slogan}', {new_edition.to_rank})")
        new_edition_cursor.commit()
        for participant in new_edition.countries:
            new_entries_cursor = connecting.cursor()
            new_entries_cursor.execute(f"insert into entries (Year, Country) values ({new_edition.year}, '{participant}')")
            new_entries_cursor.commit()
            entries_editions_cursor = connecting.cursor()
            entries_editions_cursor.execute(f"insert into EntryEdition (EntryID, EditionID) values "
                                            f"((select EntryID from entries where Country = '{participant}' and year "
                                            f"= {new_edition.year}), "
                                            f"(select EditionID from editions where Year = {new_edition.year}))")
            entries_editions_cursor.commit()
            all_artists_cursor = connecting.cursor()
            all_artists_cursor.execute("select name from Artist")
            all_artists_cursor = all_artists_cursor.fetchall()
            if (f"('{new_edition.artists[participant]}')" not in all_artists_cursor
                    and new_edition.artists[participant] != ""):
                new_artist = connecting.cursor()
                new_artist.execute(f"insert into Artist (Name) values ('{new_edition.artists[participant]}')")
                new_artist.commit()
            if new_edition.songs[participant] == "":
                new_edition.songs[participant] = None
            if new_edition.songwriters[participant] == "":
                new_edition.songwriters[participant] = None
            if new_edition.authors[participant] == "":
                new_edition.authors[participant] = None
            new_songs_cursor = connecting.cursor()
            new_songs_cursor.execute(f"insert into Song (Name, Songwriter, Author) values "
                                     f"('{new_edition.songs[participant]}', '{new_edition.songwriters[participant]}', "
                                     f"'{new_edition.authors[participant]}')")
            new_songs_cursor.commit()
            song_id = connecting.cursor()
            song_id.execute("select max(SongID) from Song")
            song_id = song_id.fetchone()
            for id in song_id:
                song_id = id
            song_entry_cursor = connecting.cursor()
            song_entry_cursor.execute(f"insert into SongEntry (SongID, EntryID) values ({song_id}, "
                                      f"(select EntryID from entries where "
                                      f"year = {new_edition.year} and country = '{participant}'))")
            song_entry_cursor.commit()
            song_artist_cursor = connecting.cursor()
            song_artist_cursor.execute(f"insert into SongArtist (SongID, ArtistID) values ({song_id}, (select ArtistID "
                                       f"from Artist where name = '{new_edition.artists[participant]}'))")
            song_artist_cursor.commit()
            country_entry_cursor = connecting.cursor()
            country_entry_cursor.execute(f"insert into CountryEntry (CountryID, EntryID) values "
                                         f"((select CountryID from Country where name = '{participant}'), "
                                         f"(select EntryID from entries where year = {new_edition.year} "
                                         f"and country = '{participant}'))")
            country_entry_cursor.commit()
            all_broadcasters_cursor = connecting.cursor()
            all_broadcasters_cursor.execute("select name from Broadcaster")
            all_broadcasters_cursor = all_broadcasters_cursor.fetchall()
            if (f"('{new_edition.broadcasters[participant]}')" not in all_broadcasters_cursor
                    and new_edition.broadcasters[participant] != ""):
                new_broadcaster = connecting.cursor()
                new_broadcaster.execute(f"insert into Broadcaster (Name) values ('{new_edition.broadcasters[participant]}')")
                new_broadcaster.commit()
            broadcaster_entry_cursor = connecting.cursor()
            broadcaster_entry_cursor.execute(f"insert into BroadcasterEntry (BroadcasterID, EntryID) values "
                                             f"((select BroadcasterID from Broadcaster where "
                                             f"Name = '{new_edition.broadcasters[participant]}'), "
                                             f"(select EntryID from entries where year = {new_edition.year} "
                                             f"and country = '{participant}'))")
            broadcaster_entry_cursor.commit()
            results_cursor = connecting.cursor()
            results_cursor.execute(f"insert into Result (EntryID, SF, SFPlace, SFPoints, FPlace, FPoints) values "
                                   f"((select EntryID from entries where year = {new_edition.year} "
                                   f"and country = '{participant}'), '{new_edition.sf[participant]}', "
                                   f"'{new_edition.sf_place[participant]}', '{new_edition.sf_points[participant]}', "
                                   f"'{new_edition.f_place[participant]}', '{new_edition.f_points[participant]}')")
            results_cursor.commit()
        if new_edition.n_of_sf1_countries == "":
            new_edition.n_of_sf1_countries = 0
        if new_edition.n_of_sf2_countries == "":
            new_edition.n_of_sf2_countries = 0
        if new_edition.n_of_f_countries == "":
            new_edition.n_of_f_countries = 0
        num_of_countries_cursor = connecting.cursor()
        num_of_countries_cursor.execute(f"insert into NumbersOfEntries (EditionID, SF1, SF2, Final, Total) "
                                        f"values ((select EditionID from editions where Year = {new_edition.year}), "
                                        f"{new_edition.n_of_sf1_countries}, {new_edition.n_of_sf2_countries}, "
                                        f"{new_edition.n_of_f_countries}, {new_edition.n_of_countries})")
        num_of_countries_cursor.commit()
        winner_id_cursor = connecting.cursor()
        winner_id_cursor.execute(f"select Entries.EntryID from result left join Entries on result.EntryID = "
                                 f"Entries.EntryID where FPlace = 1 and year = {new_edition.year}")
        winner_id_cursor = winner_id_cursor.fetchone()
        if winner_id_cursor is not None:
            winner_cursor = connecting.cursor()
            winner_cursor.execute(f"insert into Winners (Year, Country, Song, Artist) values ({new_edition.year}, "
                                  f"(select country from entries where EntryID = {winner_id_cursor}), (select name from "
                                  f"song left join SongEntry on Song.SongID = SongEntry.SongID where EntryID = "
                                  f"{winner_id_cursor}), (select name from Artist left join SongArtist on Artist.ArtistID "
                                  f"= SongArtist.ArtistID left join Song on Song.SongID = SongArtist.SongID left join "
                                  f"SongEntry on Song.SongID = SongEntry.SongID left join Entries on Entries.EntryID = "
                                  f"SongEntry.EntryID where Entries.EntryID = {winner_id_cursor}))")
            winner_cursor.commit()
            winner_edition_cursor = connecting.cursor()
            winner_edition_cursor.execute(f"insert into WinnerEdition (WinnerID, EditionID) values ((select WinnerID from "
                                          f"Winners where year = {new_edition.year}), (select EditionID from Editions "
                                          f"where year = {new_edition.year}))")
            winner_edition_cursor.commit()
        return redirect('/home')
    return render_template("add_edition.html", access=current_user.get_access(),
                           current_cursor=current_cursor)


@app.route('/about_<year>')
def about_year(year):
    if current_user.anonim():
        return render_template("404.html")
    current_cursor = []
    edition_cursor = connecting.cursor()
    edition_cursor.execute('select Editions.Year, HostCity, HostCountry, Venue, Slogan, Country, Song, Artist, Total '
                           'from editions left join NumbersOfEntries '
                           'on editions.EditionID = NumbersOfEntries.EditionID '
                           'left join WinnerEdition on WinnerEdition.EditionID = editions.EditionID '
                           'left join Winners on WinnerEdition.WinnerID = winners.WinnerID '
                           'where Editions.Year = ' + year)
    for curs in edition_cursor:
        for i in range(9):
            current_cursor.append(curs[i])
    keys = ['Year', 'Host City', 'Host Country', 'Venue', 'Slogan', 'Winning Country',
            'Winning Song', 'Winning Artist', 'Countries Participating']
    countries_cursor = connecting.cursor()
    countries_cursor.execute('select Year, Country, Song.Name, Artist.Name, Songwriter, Author from entries '
                             'left join SongEntry on entries.EntryID = SongEntry.EntryID '
                             'left join Song on Song.SongID = SongEntry.SongID '
                             'left join SongArtist on Song.SongID = SongArtist.SongID '
                             'left join Artist on SongArtist.ArtistID = Artist.ArtistID where year = ' + year)
    countries = countries_cursor.fetchall()
    results_cursor = connecting.cursor()
    results_cursor.execute('select Year, Entries.Country, Broadcaster.Name, Song.Name, Artist.Name, '
                           'FPlace, FPoints, SFPlace, SFPoints from entries '
                           'left join SongEntry on entries.EntryID = SongEntry.EntryID '
                           'left join Song on Song.SongID = SongEntry.SongID '
                           'left join BroadcasterEntry on BroadcasterEntry.EntryID = Entries.EntryID '
                           'left join Broadcaster on Broadcaster.BroadcasterID = BroadcasterEntry.BroadcasterID '
                           'left join SongArtist on Song.SongID = SongArtist.SongID '
                           'left join Artist on SongArtist.ArtistID = Artist.ArtistID '
                           'left join Result on Result.EntryID = entries.EntryID where year = ' + year)
    results = results_cursor.fetchall()
    return render_template("more_about_year.html", current_cursor=current_cursor,
                           results=results, countries=countries,
                           year=year, keys=keys, access=current_user.get_access())


@app.route('/edit_<year>', methods=["GET", "POST"])
def edit_year(year):
    if current_user.anonim():
        return render_template("404.html")
    if not current_user.admin():
        return render_template("404.html", access=current_user.get_access())
    current_cursor = []
    countries_cursor = connecting.cursor()
    countries_cursor.execute(f"select country from entries where year = {year}")
    for curs in countries_cursor:
        for i in range(1):
            current_cursor.append(curs[i])
    if request.method == "POST":
        if request.form['HostCity'] != "":
            host_city = request.form['HostCity']
            update_host_city_cursor = connecting.cursor()
            update_host_city_cursor.execute(f"update Editions set HostCity = '{host_city}' where year = {year}")
            update_host_city_cursor.commit()
        if request.form['HostCountry'] != "":
            host_country = request.form['HostCountry']
            update_host_country_cursor = connecting.cursor()
            update_host_country_cursor.execute(f"update Editions set HostCountry = '{host_country}' where year = {year}")
            update_host_country_cursor.commit()
        if request.form['Venue'] != "":
            venue = request.form['Venue']
            update_venue_cursor = connecting.cursor()
            update_venue_cursor.execute(f"update Editions set venue = '{venue}' where year = {year}")
            update_venue_cursor.commit()
        if request.form['Slogan'] != "":
            slogan = request.form['Slogan']
            update_slogan_cursor = connecting.cursor()
            update_slogan_cursor.execute(f"update Editions set slogan = '{slogan}' where year = {year}")
            update_slogan_cursor.commit()
        if request.form['toRank'] != "":
            to_rank = request.form['toRank']
            update_to_rank_cursor = connecting.cursor()
            update_to_rank_cursor.execute(f"update Editions set toRank = '{to_rank}' where year = {year}")
            update_to_rank_cursor.commit()
        if request.form['Number of participants'] != "":
            num_of_countries = request.form['Number of participants']
            update_total_cursor = connecting.cursor()
            update_total_cursor.execute(f"update NumbersOfEntries set total = {num_of_countries} where EditionID = "
                                        f"(select EditionID from editions where year = {year})")
            update_total_cursor.commit()
        if request.form['Number of participants in SF1'] != "":
            num_of_sf1_countries = request.form['Number of participants in SF1']
            update_sf1_cursor = connecting.cursor()
            update_sf1_cursor.execute(f"update NumbersOfEntries set SF1 = {num_of_sf1_countries} where EditionID = "
                                      f"(select EditionID from editions where year = {year})")
            update_sf1_cursor.commit()
        if request.form['Number of participants in SF2'] != "":
            num_of_sf2_countries = request.form['Number of participants in SF2']
            update_sf2_cursor = connecting.cursor()
            update_sf2_cursor.execute(f"update NumbersOfEntries set SF2 = {num_of_sf2_countries} where EditionID = "
                                      f"(select EditionID from editions where year = {year})")
            update_sf2_cursor.commit()
        if request.form['Number of participants in final'] != "":
            num_of_f_countries = request.form['Number of participants in final']
            update_f_cursor = connecting.cursor()
            update_f_cursor.execute(f"update NumbersOfEntries set final = {num_of_f_countries} where EditionID = "
                                    f"(select EditionID from editions where year = {year})")
            update_f_cursor.commit()
        participants = request.form.getlist('participating_countries[]')
        print(participants)
        if "Other" in participants:
            participants.remove("Other")
            missing_participants = request.form.getlist('MissingCountry')
            for participant in missing_participants:
                print(participant)
                if participant != "":
                    if participant[0] == " ":
                        error_message = "Invalid country"
                        return render_template("add_edition.html", access=current_user.get_access(),
                                               error_message=error_message, current_cursor=current_cursor)
                    if participant not in current_cursor:
                        countries_cursor = connecting.cursor()
                        countries_cursor.execute(f"insert into country (name, DebutYear) values "
                                                 f"('{participant}', {year})")
                        countries_cursor.commit()
                    new_entries_cursor = connecting.cursor()
                    new_entries_cursor.execute(
                        f"insert into entries (Year, Country) values ({year}, '{participant}')")
                    new_entries_cursor.commit()
                    entries_editions_cursor = connecting.cursor()
                    entries_editions_cursor.execute(f"insert into EntryEdition (EntryID, EditionID) values "
                                                    f"((select EntryID from entries where Country = '{participant}' and year "
                                                    f"= {year}), "
                                                    f"(select EditionID from editions where Year = {year}))")
                    entries_editions_cursor.commit()
                    all_artists_cursor = connecting.cursor()
                    all_artists_cursor.execute("select name from Artist")
                    all_artists_cursor = all_artists_cursor.fetchall()
                    if (f"('{request.form[participant + 'artist']}')" not in all_artists_cursor
                            and request.form[participant + 'artist'] != ""):
                        new_artist = connecting.cursor()
                        new_artist.execute(f"insert into Artist (Name) values ('{request.form[participant + 'artist']}')")
                        new_artist.commit()
                    if (request.form[participant + 'song'] != "" and request.form[participant + 'songwriter'] != ""
                            and request.form[participant + 'author'] != ""):
                        new_songs_cursor = connecting.cursor()
                        new_songs_cursor.execute(f"insert into Song (Name, Songwriter, Author) values "
                                                 f"('{request.form[participant + 'song']}', "
                                                 f"'{request.form[participant + 'songwriter']}', "
                                                 f"'{request.form[participant + 'author']}')")
                        new_songs_cursor.commit()
                        song_entry_cursor = connecting.cursor()
                        song_entry_cursor.execute(
                            f"insert into SongEntry (SongID, EntryID) values ((select SongID from song "
                            f"where name = '{request.form[participant + 'song']}' "
                            f"and songwriter = '{request.form[participant + 'songwriter']}' "
                            f"and author = '{request.form[participant + 'author']}'), "
                            f"(select EntryID from entries where "
                            f"year = {year} and country = '{participant}'))")
                        song_entry_cursor.commit()
                        song_artist_cursor = connecting.cursor()
                        song_artist_cursor.execute(f"insert into SongArtist (SongID, ArtistID) values "
                                                   f"((select SongID from songs where name = '{request.form[participant + 'song']}' "
                                                   f"and songwriter = '{request.form[participant + 'songwriter']}' "
                                                   f"and author = '{request.form[participant + 'author']}'), "
                                                   f"(select ArtistID from Artist where name = '{request.form[participant + 'artist']}'))")
                        song_artist_cursor.commit()
                    country_entry_cursor = connecting.cursor()
                    country_entry_cursor.execute(f"insert into CountryEntry (CountryID, EntryID) values "
                                                 f"((select CountryID from Country where name = '{participant}'), "
                                                 f"(select EntryID from entries where year = {year} "
                                                 f"and country = '{participant}'))")
                    country_entry_cursor.commit()
                    all_broadcasters_cursor = connecting.cursor()
                    all_broadcasters_cursor.execute("select name from Broadcaster")
                    all_broadcasters_cursor = all_broadcasters_cursor.fetchall()
                    if (f"('{request.form[participant + 'broadcaster']}')" not in all_broadcasters_cursor
                            and request.form[participant + 'broadcaster'] != ""):
                        new_broadcaster = connecting.cursor()
                        new_broadcaster.execute(
                            f"insert into Broadcaster (Name) values ('{request.form[participant + 'broadcaster']}')")
                        new_broadcaster.commit()
                    broadcaster_entry_cursor = connecting.cursor()
                    broadcaster_entry_cursor.execute(f"insert into BroadcasterEntry (BroadcasterID, EntryID) values "
                                                     f"((select BroadcasterID from Broadcaster where "
                                                     f"Name = '{request.form[participant + 'broadcaster']}'), "
                                                     f"(select EntryID from entries where year = {year} "
                                                     f"and country = '{participant}'))")
                    broadcaster_entry_cursor.commit()
                    results_cursor = connecting.cursor()
                    results_cursor.execute(
                        f"insert into Result (EntryID, SF, SFPlace, SFPoints, FPlace, FPoints) values "
                        f"((select EntryID from entries where year = {year} "
                        f"and country = '{participant}'), '{request.form[participant + 'SF']}', "
                        f"'{request.form[participant + 'SFPlace']}', '{request.form[participant + 'SFPoints']}', "
                        f"'{request.form[participant + 'FPlace']}', '{request.form[participant + 'FPoints']}')")
                    results_cursor.commit()
        for participant in participants:
            print(participant)
            if request.form[participant + 'artist'] != "":
                print(9)
                artist = request.form[participant + 'artist']
                all_artists_cursor = connecting.cursor()
                all_artists_cursor.execute("select name from Artist")
                all_artists_cursor = all_artists_cursor.fetchall()
                if f"('{artist}')" not in all_artists_cursor:
                    new_artist = connecting.cursor()
                    new_artist.execute(f"insert into Artist (Name) values ('{artist}')")
                    new_artist.commit()
                update_artist_cursor = connecting.cursor()
                update_artist_cursor.execute(f"update SongArtist set ArtistID = (select ArtistID from Artist where "
                                             f"name = '{artist}') where SongID = (select SongID from SongEntry where "
                                             f"EntryID = (select EntryID from Entries where year = {year} and Country "
                                             f"= '{participant}'))")
                update_artist_cursor.commit()
            if request.form[participant + 'song'] != "":
                song = request.form[participant + 'song']
                update_song_cursor = connecting.cursor()
                update_song_cursor.execute(f"update song set name = '{song}' where SongID = (select SongID from "
                                           f"SongEntry where EntryID = (select EntryID from entries where year = "
                                           f"{year} and Country = '{participant}'))")
                update_song_cursor.commit()
            if request.form[participant + 'songwriter'] != "":
                songwriter = request.form[participant + 'songwriter']
                update_songwriter_cursor = connecting.cursor()
                update_songwriter_cursor.execute(f"update song set name = '{songwriter}' where SongID = (select SongID "
                                                 f"from SongEntry where EntryID = (select EntryID from entries where "
                                                 f"year = {year} and Country = '{participant}'))")
                update_songwriter_cursor.commit()
            if request.form[participant + 'author'] != "":
                author = request.form[participant + 'author']
                update_author_cursor = connecting.cursor()
                update_author_cursor.execute(f"update song set name = '{author}' where SongID = (select SongID from "
                                             f"SongEntry where EntryID = (select EntryID from entries where year = "
                                             f"{year} and Country = '{participant}'))")
                update_author_cursor.commit()
            if request.form[participant + 'broadcaster'] != "":
                broadcaster = request.form[participant + 'broadcaster']
                all_broadcasters_cursor = connecting.cursor()
                all_broadcasters_cursor.execute("select name from Artist")
                all_broadcasters_cursor = all_broadcasters_cursor.fetchall()
                if f"('{broadcaster}')" not in all_broadcasters_cursor:
                    new_broadcaster = connecting.cursor()
                    new_broadcaster.execute(f"insert into Broadcaster (Name) values ('{broadcaster}')")
                    new_broadcaster.commit()
                update_broadcaster_entry_cursor = connecting.cursor()
                update_broadcaster_entry_cursor.execute(f"update BroadcasterEntry set BroadcasterID = (select "
                                                        f"BroadcasterID from Broadcaster where name = '{broadcaster}')"
                                                        f" where EntryID = (select EntryID from entries where year = "
                                                        f"{year} and Country = '{participant}')")
                update_broadcaster_entry_cursor.commit()
            if request.form[participant + 'SF'] != "":
                sf = request.form[participant + 'SF']
                sf_cursor = connecting.cursor()
                sf_cursor.execute(f"update result set sf = {sf} where EntryID = (select EntryID from entries where "
                                  f"year = {year} and country = '{participant}')")
                sf_cursor.commit()
            if request.form[participant + 'SFPlace'] != "":
                sf_place = request.form[participant + 'SFPlace']
                sf_place_cursor = connecting.cursor()
                sf_place_cursor.execute(f"update result set sfplace = {sf_place} where EntryID = (select EntryID from "
                                        f"entries where year = {year} and country = '{participant}')")
                sf_place_cursor.commit()
            if request.form[participant + 'SFPoints'] != "":
                sf_points = request.form[participant + 'SFPoints']
                sf_points_cursor = connecting.cursor()
                sf_points_cursor.execute(f"update result set sfpoints = {sf_points} where EntryID = (select EntryID from "
                                         f"entries where year = {year} and country = '{participant}')")
                sf_points_cursor.commit()
            if request.form[participant + 'FPlace'] != "":
                print(7)
                f_place = request.form[participant + 'FPlace']
                f_place_cursor = connecting.cursor()
                f_place_cursor.execute(f"update result set fplace = {f_place} where EntryID = (select EntryID from "
                                       f"entries where year = {year} and country = '{participant}')")
                f_place_cursor.commit()
            if request.form[participant + 'FPoints'] != "":
                f_points = request.form[participant + 'FPoints']
                f_points_cursor = connecting.cursor()
                f_points_cursor.execute(
                    f"update result set fpoints = {f_points} where EntryID = (select EntryID from "
                    f"entries where year = {year} and country = '{participant}')")
                f_points_cursor.commit()
        return redirect('/home')
    return render_template("edit_year.html", year=year, access=current_user.get_access(),
                           current_cursor=current_cursor)


@app.route('/delete_<year>_for_ranking')
def delete_edition_for_ranking(year):
    if current_user.anonim():
        return render_template("404.html")
    if not current_user.admin():
        return render_template("404.html", access=current_user.get_access())
    cursor = connecting.cursor()
    cursor.execute("UPDATE editions SET toRank = "
                   "CASE WHEN toRank = 1 THEN 0 "
                   "WHEN toRank = 0 THEN 1 "
                   "ELSE toRank END "
                   "where year = " + year)
    cursor.close()
    connecting.commit()
    return redirect('/home')


@app.route('/rank_<year>', methods=['GET', 'POST'])
def rank_edition(year):
    if current_user.anonim():
        return render_template("404.html")
    check_ranking_cursor = connecting.cursor()
    check_ranking_cursor.execute("select * from rankings where UserID = (select UserID from users where Login = '" +
                                 current_user.get_username() + "') and EditionID = (select EditionID from editions "
                                                               'where Year = ' + year + ')')
    if check_ranking_cursor.fetchone() is not None:
        return redirect('/ranked_' + year)
    current_cursor = []
    edition_countries_cursor = connecting.cursor()
    edition_countries_cursor.execute('select Country from Entries where Year = ' + year)
    for curs in edition_countries_cursor:
        for i in range(1):
            current_cursor.append(curs[i])
    number_of_participants_cursor = connecting.cursor()
    number_of_participants_cursor.execute('select Total from Editions left join NumbersOfEntries '
                                          'on Editions.EditionID = NumbersOfEntries.EditionID where Year = ' + year)
    for curs in number_of_participants_cursor:
        for i in range(1):
            number_of_participants_cursor = int(curs[i])
    half = round(number_of_participants_cursor / 2)
    results_cursor = connecting.cursor()
    results_cursor.execute('select Year, Entries.Country, Song.Name, artist.Name from entries '
                           'left join SongEntry on entries.EntryID = SongEntry.EntryID '
                           'left join Song on Song.SongID = SongEntry.SongID '
                           'left join BroadcasterEntry on BroadcasterEntry.EntryID = Entries.EntryID '
                           'left join Broadcaster on Broadcaster.BroadcasterID = BroadcasterEntry.BroadcasterID '
                           'left join SongArtist on Song.SongID = SongArtist.SongID '
                           'left join Artist on SongArtist.ArtistID = Artist.ArtistID '
                           'left join Result on Result.EntryID = entries.EntryID where year = ' + year)
    results = results_cursor.fetchall()
    if request.method == 'POST':
        data = {}
        points = {1: 12, 2: 10, 3: 8, 4: 7, 5: 6, 6: 5, 7: 4, 8: 3, 9: 2, 10: 1}
        for i in range(number_of_participants_cursor):
            data[i + 1] = request.form[str(i)]
            if i + 1 > 10:
                points[i + 1] = 0
        for position, country in data.items():
            print(position)
            ranking_cursor = connecting.cursor()
            ranking_cursor.execute("insert into ranks (Rank, EntryID, UserID, points) "
                                   "values (" + str(position) + ", "
                                   "(select EntryId from entries where Year = " + str(year) + " and country = '"
                                   + country + "'), "
                                   "(select UserID from Users where Login = '" + current_user.get_username() + "'), "
                                   + str(points[position]) + ")")
            ranking_cursor.commit()
        json_filename = current_user.get_username() + "_" + str(year) + ".json"
        with open(json_filename, "w") as outfile:
            json.dump(data, outfile)
        with open(json_filename) as d:
            save_ranking_cursor = connecting.cursor()
            save_ranking_cursor.execute("insert into rankings (UserID, EditionID, ranking) values "
                                        "((select UserID from users where login = '" + current_user.get_username() + "'), "
                                        "(select EditionID from editions where Year = " + year + "), '" +
                                        d.read() + "')")
            save_ranking_cursor.commit()
        return redirect('/ranked_' + str(year))
    return render_template("rank_edition.html", current_cursor=current_cursor,
                           number_of_participants=number_of_participants_cursor, results=results,
                           year=year, access=current_user.get_access(), half=half)


@app.route('/ranked_<year>')
def ranked_year(year):
    if current_user.anonim():
        return render_template("404.html")
    json_filename = current_user.get_username() + "_" + str(year) + ".json"
    with open(json_filename) as d:
        print(d.read())
    with open(json_filename) as d:
        ranking = json.load(d)
    half = int(len(ranking)/2)
    return render_template("ranked_edition.html", file=json_filename, year=year, ranking=ranking,
                           access=current_user.get_access(), str=str, len=len, half=half)


@app.route('/update_<year>_ranking', methods=["GET", "POST"])
def update_ranking(year):
    if current_user.anonim():
        return render_template("404.html")
    json_filename = current_user.get_username() + "_" + str(year) + ".json"
    with open(json_filename) as d:
        ranking = json.load(d)
    current_cursor = []
    edition_countries_cursor = connecting.cursor()
    edition_countries_cursor.execute('select Country from Entries where Year = ' + year)
    for curs in edition_countries_cursor:
        for i in range(1):
            current_cursor.append(curs[i])
    number_of_participants_cursor = connecting.cursor()
    number_of_participants_cursor.execute('select Total from Editions left join NumbersOfEntries '
                                          'on Editions.EditionID = NumbersOfEntries.EditionID where Year = ' + year)
    for curs in number_of_participants_cursor:
        for i in range(1):
            number_of_participants_cursor = int(curs[i])
    half = round(number_of_participants_cursor / 2)
    results_cursor = connecting.cursor()
    results_cursor.execute('select Year, Entries.Country, Song.Name, Artist.Name from entries '
                           'left join SongEntry on entries.EntryID = SongEntry.EntryID '
                           'left join Song on Song.SongID = SongEntry.SongID '
                           'left join BroadcasterEntry on BroadcasterEntry.EntryID = Entries.EntryID '
                           'left join Broadcaster on Broadcaster.BroadcasterID = BroadcasterEntry.BroadcasterID '
                           'left join SongArtist on Song.SongID = SongArtist.SongID '
                           'left join Artist on SongArtist.ArtistID = Artist.ArtistID '
                           'left join Result on Result.EntryID = entries.EntryID where year = ' + year)
    results = results_cursor.fetchall()
    if request.method == "POST":
        for i in range(number_of_participants_cursor):
            ranking[i + 1] = request.form[str(i)]
            points = {1: 12, 2: 10, 3: 8, 4: 7, 5: 6, 6: 5, 7: 4, 8: 3, 9: 2, 10: 1}
            if i + 1 > 10:
                points[i + 1] = 0
            ranking_cursor = connecting.cursor()
            ranking_cursor.execute("update ranks set rank = " + str(i + 1) + " where EntryID = "
                                   "(select EntryID from entries where Country = '" +
                                   ranking[i + 1] + "' and Year = " + year + ") and UserID = "
                                   "(select UserID from users where Login = '" + current_user.get_username() + "')")
            ranking_cursor.commit()
            ranking_points_cursor = connecting.cursor()
            ranking_points_cursor.execute("update ranks set points = " + str(points[i + 1]) + " where EntryID = "
                                          "(select EntryID from entries where Country = '" +
                                          ranking[i + 1] + "' and Year = " + year + ") and UserID = "
                                          "(select UserID from users where Login = '" + current_user.get_username() + "')")
        with open(json_filename, "w") as outfile:
            json.dump(ranking, outfile)
        return redirect('/ranked_' + year)
    return render_template("rank_edition.html", access=current_user.get_access(), ranking=ranking,
                           current_cursor=current_cursor, number_of_participants=number_of_participants_cursor,
                           year=year, str=str, half=half, results=results)


@app.route('/delete_<year>_ranking')
def delete_ranking(year):
    delete_ranking_cursor = connecting.cursor()
    delete_ranking_cursor.execute("delete from rankings where UserID = (select UserID from Users where Login = '"
                                  + current_user.get_username() + "') and EditionID = (select EditionID from Editions"
                                                                  " where Year = " + str(year) + ")")
    delete_ranking_cursor.commit()
    delete_ranks_cursor = connecting.cursor()
    delete_ranks_cursor.execute("delete from ranks where UserID = (select UserID from Users where Login = '"
                                + current_user.get_username() + "') and EntryID in (select EntryID from EntryEdition"
                                " where EditionID in (select EditionID from editions where year = " + str(year) + "))")
    delete_ranks_cursor.commit()
    return redirect('/my_profile')


@app.route('/community_rank_<year>', methods=["POST", "GET"])
def community(year):
    if current_user.anonim():
        return render_template("404.html")
    total_rankings = connecting.cursor()
    total_rankings.execute(f"select * from rankings where EditionID = "
                           f"(select EditionID from editions where year = {year})")
    total_rankings = total_rankings.fetchall()
    total_rankings = total_rankings.__len__()
    if total_rankings == 0:
        message = "Noone ranked this edition yet"
        return render_template("community_rank.html", year=year, access=current_user.get_access(),
                               message=message)
    adding = ""
    community_rank = connecting.cursor()
    community_rank_query = (("select country, round(AVG(rank), 2) from ranks "
                             "left join entries on ranks.EntryID = entries.EntryID "
                             "left join EntryEdition on entries.EntryID = EntryEdition.EditionID "
                             "where ranks.EntryID in (select EntryID from EntryEdition where EditionID = "
                             "(select EditionID from editions where year = ")
                            + year + ")) group by Country order by AVG(rank)")
    community_rank.execute(community_rank_query)
    community_rank = community_rank.fetchall()
    d_s = []
    for country in community_rank:
        ranks_cursor = connecting.cursor()
        ranks_cursor.execute(f"select rank from ranks left join entries on ranks.EntryID = entries.EntryID "
                             f"where country = '{country[0]}' and year = {year}")
        ranks = ranks_cursor.fetchall()
        d = 0
        for rank in ranks:
            d += (int(rank[0]) - country[1]) ** 2
        d = d / len(ranks)
        print(country[0], d)
        d_s.append(d)
    print(d_s)
    min_variance = min(d_s)
    max_variance = max(d_s)

    min_index = d_s.index(min_variance)
    max_index = d_s.index(max_variance)

    min_variable = community_rank[min_index][0]
    max_variable = community_rank[max_index][0]

    print("Minimum variance:", min_variance)
    print("Corresponding random variable:", min_variable)

    print("Maximum variance:", max_variance)
    print("Corresponding random variable:", max_variable)

    community_points_rank = connecting.cursor()
    community_points_rank_query = (("select country, sum(points) from ranks "
                                    "left join entries on ranks.EntryID = entries.EntryID "
                                    "left join EntryEdition on entries.EntryID = EntryEdition.EditionID "
                                    "where ranks.EntryID in (select EntryID from EntryEdition where EditionID = "
                                    "(select EditionID from editions where year = ")
                                    + year + ")) group by Country order by sum(points) desc")
    community_points_rank.execute(community_points_rank_query)
    community_points_rank = community_points_rank.fetchall()
    print(community_points_rank)
    total_rankings = connecting.cursor()
    total_rankings.execute(f"select * from rankings where EditionID = "
                           f"(select EditionID from editions where year = {year})")
    total_rankings = total_rankings.fetchall()
    total_rankings = total_rankings.__len__()
    if total_rankings == 0:
        message = "Noone ranked this edition yet"
        return render_template("community_rank.html", year=year, access=current_user.get_access(),
                               community_rank=community_rank, message=message)
    if request.method == "POST":
        age = request.form['age']
        zodiac_sign = request.form['Zodiac Sign']
        gender = request.form['Gender']
        country = request.form['Country']
        if age != "" or zodiac_sign != "" or gender != "" or country != "":
            adding = " and UserID in (select UserID from users where "
        if zodiac_sign != "":
            adding += "ZodiacSign = '" + zodiac_sign + "'"
            if age != "" or gender != "" or country != "":
                adding += " and "
        if country != "":
            adding += "Country = '" + country + "'"
            if age != "" or gender != "":
                adding += " and "
        if gender != "":
            adding += "Gender = '" + gender + "'"
            if age != "":
                adding += " and "
        if age != "":
            if age == "6-12":
                adding += "Age > 5 and Age < 13"
            if age == "13-17":
                adding += "Age > 12 and Age < 18"
            if age == "18-25":
                adding += "Age > 17 and Age < 26"
            if age == "26-35":
                adding += "Age > 25 and Age < 36"
            if age == "36-45":
                adding += "Age > 35 and Age < 46"
            if age == "46-55":
                adding += "Age > 45 and Age < 56"
            if age == "56-65":
                adding += "Age > 55 and Age < 66"
            if age == "66-75":
                adding += "Age > 65 and Age < 76"
            if age == "76-85":
                adding += "Age > 75 and Age < 86"
            if age == "Older":
                adding += "Age > 85"
        if age != "" or zodiac_sign != "" or gender != "" or country != "":
            adding += ") "
        community_rank_query = (("select country, round(AVG(rank), 2) from ranks "
                                 "left join entries on ranks.EntryID = entries.EntryID "
                                 "left join EntryEdition on entries.EntryID = EntryEdition.EditionID "
                                 "where ranks.EntryID in (select EntryID from EntryEdition where EditionID = "
                                 "(select EditionID from editions where year = ")
                                + year + "))" + adding + "group by Country order by AVG(rank)")
        community_rank = connecting.cursor()
        community_rank.execute(community_rank_query)
        community_rank = community_rank.fetchall()
        d_s = []
        for country in community_rank:
            ranks_cursor = connecting.cursor()
            ranks_cursor.execute(f"select rank from ranks left join entries on ranks.EntryID = entries.EntryID "
                                 f"where country = '{country[0]}' and year = {year}")
            ranks = ranks_cursor.fetchall()
            d = 0
            for rank in ranks:
                d += (int(rank[0]) - country[1]) ** 2
            d = d / len(ranks)
            print(country[0], d)
            d_s.append(d)
        print(d_s)
        print(community_rank[0][0])
        min_variance = min(d_s)
        max_variance = max(d_s)

        min_index = d_s.index(min_variance)
        max_index = d_s.index(max_variance)

        min_variable = community_rank[min_index][0]
        max_variable = community_rank[max_index][0]

        print("Minimum variance:", min_variance)
        print("Corresponding random variable:", min_variable)

        print("Maximum variance:", max_variance)
        print("Corresponding random variable:", max_variable)

        community_points_rank = connecting.cursor()
        community_points_rank_query = (("select country, sum(points) from ranks "
                                        "left join entries on ranks.EntryID = entries.EntryID "
                                        "left join EntryEdition on entries.EntryID = EntryEdition.EditionID "
                                        "where ranks.EntryID in (select EntryID from EntryEdition where EditionID = "
                                        "(select EditionID from editions where year = ")
                                       + year + "))" + adding + "group by Country order by sum(points) desc")
        community_points_rank.execute(community_points_rank_query)
        community_points_rank = community_points_rank.fetchall()

        total_rankings = connecting.cursor()
        total_rankings.execute(f"select * from rankings where EditionID = "
                               f"(select EditionID from editions where year = {year})" + adding)
        total_rankings = total_rankings.fetchall()
        total_rankings = total_rankings.__len__()
        print(total_rankings)
        if total_rankings == 0:
            filter_message = "Noone in this category ranked this edition yet"
            return render_template("community_rank.html", year=year, access=current_user.get_access(),
                                   community_rank=community_rank, filter_message=filter_message, age=age, gender=gender,
                                   country=country, zodiac_sign=zodiac_sign, community_points_rank=community_points_rank)
        return render_template("community_rank.html", year=year, access=current_user.get_access(),
                               community_rank=community_rank, age=age, gender=gender,
                               country=country, zodiac_sign=zodiac_sign, N=total_rankings, least_divisive=min_variable,
                               most_divisive=max_variable, community_points_rank=community_points_rank)
    return render_template("community_rank.html", year=year, access=current_user.get_access(),
                           community_rank=community_rank, N=total_rankings, least_divisive=min_variable,
                           most_divisive=max_variable, community_points_rank=community_points_rank)


@app.route('/my_profile', methods=["GET", "POST"])
def profile():
    if current_user.anonim():
        return render_template("404.html")
    current_cursor = []
    keys = ['Name', 'Zodiac Sign', 'Gender', 'Country', 'Age']
    cursor = connecting.cursor()
    cursor.execute("SELECT Login, ZodiacSign, Gender, Country, Age FROM Users where Login = '"
                   + current_user.get_username() + "'")
    for curs in cursor:
        current_cursor.append(curs)
    rankings_cursor = connecting.cursor()
    rankings_cursor.execute("select year, HostCity, HostCountry from editions right join rankings "
                            "on rankings.EditionID = editions.EditionID "
                            "left join Users on Users.UserID = rankings.UserID "
                            "where login = '" + current_user.get_username() + "'")
    rankings = rankings_cursor.fetchall()
    users_winners_cursor = connecting.cursor()
    users_winners_cursor.execute(f"select year, entries.Country from entries left join ranks "
                                 f"on ranks.EntryID = entries.EntryID left join users on ranks.UserID = users.UserID "
                                 f"where login = '{current_user.get_username()}' and rank = 1 order by year desc")
    users_winners = users_winners_cursor.fetchall()
    fav_countries_cursor = connecting.cursor()
    fav_countries_cursor.execute(f"select entries.country, round(avg(rank/total)*(select count(name) from country), 2) "
                                 f"as av from ranks left join users on users.UserID = ranks.userid left join entries "
                                 f"on entries.entryid = ranks.entryid left join entryedition on entryedition.entryid "
                                 f"= entries.EntryID left join editions on entryedition.EditionID = editions.EditionID "
                                 f"left join numbersofentries on numbersofentries.EditionID = editions.editionid "
                                 f"where login = '{current_user.get_username()}' group by entries.Country order by av ")
    fav_countries = fav_countries_cursor.fetchall()
    winner_places_cursor = connecting.cursor()
    winner_places_cursor.execute(f"select editions.year, entries.country, rank from ranks left join entries "
                                 f"on ranks.EntryID = entries.EntryID left join EntryEdition "
                                 f"on EntryEdition.EntryID = Entries.EntryID left join Editions "
                                 f"on EntryEdition.EditionID = Editions.EditionID left join users "
                                 f"on ranks.UserID = users.UserID where entries.country = '{fav_countries[0][0]}' "
                                 f"and login = '{current_user.get_username()}'")
    winner_places = winner_places_cursor.fetchall()
    print(winner_places)
    if rankings.__len__() == 0:
        message = "You have no rankings yet"
        return render_template('profile.html',
                               username=current_user.get_username(), access=current_user.get_access(),
                               data=current_cursor, keys=keys, rankings=rankings, message=message)
    if request.method == "POST":
        personal_data = Authorization(current_user.get_username(), current_user.get_password())
        username = request.form['username']
        age = request.form['age']
        zodiac_sign = request.form['Zodiac Sign']
        gender = request.form['Gender']
        country = request.form['Country']
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        login_cursor = connecting.cursor()
        login_cursor.execute('SELECT Login FROM Users')
        for curs in login_cursor:
            curs = str(curs)
            personal_data.add_login(curs)
        login_cursor.close()
        password_cursor = connecting.cursor()
        password_cursor.execute('SELECT Password FROM Users')
        for curs in password_cursor:
            curs = str(curs)
            personal_data.add_password(curs)
        password_cursor.close()
        if username != "" and f"('{username}',)" not in personal_data.get_logins():
            for i in username:
                if i not in personal_data.symbols:
                    error_message = "Username can't contain '" + i + "' symbol"
                    return render_template('profile.html',
                                           username=current_user.get_username(), access=current_user.get_access(),
                                           data=current_cursor, keys=keys, rankings=rankings, error=error_message)
            new_username_cursor = connecting.cursor()
            new_username_cursor.execute(f"update users set Login = '{username}' where login = "
                                        f"'{current_user.get_username()}'")
            new_username_cursor.commit()
            current_user.set_username(username)
        elif f"('{username}',)" in personal_data.get_logins():
            error_message = "User with this login already exists"
            return render_template('profile.html',
                                   username=current_user.get_username(), access=current_user.get_access(),
                                   data=current_cursor, keys=keys, rankings=rankings, error=error_message)
        if age != "":
            age = int(age)
            if age <= 6:
                age = -1
            new_age_cursor = connecting.cursor()
            new_age_cursor.execute(f"update users set age = {age} where login = '{current_user.get_username()}'")
            new_age_cursor.commit()
        if zodiac_sign != "":
            new_zodiac_cursor = connecting.cursor()
            new_zodiac_cursor.execute(f"update users set ZodiacSign = '{zodiac_sign}' where login = "
                                      f"'{current_user.get_username()}'")
            new_zodiac_cursor.commit()
        if gender != "":
            new_gender_cursor = connecting.cursor()
            new_gender_cursor.execute(f"update users set gender = '{gender}' where login = "
                                      f"'{current_user.get_username()}'")
            new_gender_cursor.commit()
        if country != "":
            new_country_cursor = connecting.cursor()
            new_country_cursor.execute(f"update users set country = '{country}' where login = "
                                       f"'{current_user.get_username()}'")
            new_country_cursor.commit()
        if old_password != "":
            if old_password != current_user.get_password():
                error_message = "Old password is wrong"
                return render_template('profile.html',
                                       username=current_user.get_username(), access=current_user.get_access(),
                                       data=current_cursor, keys=keys, rankings=rankings, error=error_message)
            elif new_password == "" or confirm_password == "":
                error_message = "Fulfil all 3 fields to change your password!"
                return render_template('profile.html',
                                       username=current_user.get_username(), access=current_user.get_access(),
                                       data=current_cursor, keys=keys, rankings=rankings, error=error_message)
            elif new_password != confirm_password:
                error_message = "Entered new password wasn't confirmed"
                return render_template('profile.html',
                                       username=current_user.get_username(), access=current_user.get_access(),
                                       data=current_cursor, keys=keys, rankings=rankings, error=error_message)
            elif len(new_password) != 8:
                error_message = "Your password should contain 8 symbols"
                return render_template('profile.html',
                                       username=current_user.get_username(), access=current_user.get_access(),
                                       data=current_cursor, keys=keys, rankings=rankings, error=error_message)
            for i in new_password:
                if i not in personal_data.symbols:
                    error_message = "Password can't contain '" + i + "' symbol"
                    return render_template('profile.html',
                                           username=current_user.get_username(), access=current_user.get_access(),
                                           data=current_cursor, keys=keys, rankings=rankings, error=error_message)
            personal_data.set_right_password(new_password)
            encrypted_password = personal_data.crypt()
            if f"('{encrypted_password}',)" not in personal_data.get_passwords():
                new_password_cursor = connecting.cursor()
                new_password_cursor.execute(f"update users set password = '{encrypted_password}' where login = "
                                            f"'{current_user.get_username()}'")
                new_password_cursor.commit()
            elif f"('{encrypted_password}',)" in personal_data.get_passwords():
                error_message = "Your password should be unique"
                return render_template('profile.html',
                                       username=current_user.get_username(), access=current_user.get_access(),
                                       data=current_cursor, keys=keys, rankings=rankings, error=error_message)
            else:
                error_message = "Enter your old password"
                return render_template('profile.html',
                                       username=current_user.get_username(), access=current_user.get_access(),
                                       data=current_cursor, keys=keys, rankings=rankings, error=error_message)
        return redirect('/my_profile')
    return render_template('profile.html',
                           username=current_user.get_username(), access=current_user.get_access(),
                           data=current_cursor, keys=keys, rankings=rankings, winners=users_winners,
                           fav_countries=fav_countries)


if __name__ == '__main__':
    app.run(debug=False)
