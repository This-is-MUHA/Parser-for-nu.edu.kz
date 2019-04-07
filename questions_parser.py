from bs4 import BeautifulSoup
import requests
from time import sleep
from validators import url

visited_pages = []
f = open('parsed_text.txt', 'a')

def parse_link(link, level):
	try:
		if str(link)[:6] == 'mailto' or level > 2:
			return
		if str(link)[:4] in ['?uri', '/wps']:
			link = 'https://admissions.nu.edu.kz/' + str(link)
		r = requests.get(link)
		data = r.text
		soup = BeautifulSoup(data, features='html.parser')
		name = soup.find('title').contents[0]
		if name in visited_pages or name == 'Error 404':
			return
		visited_pages.append(name)
		indent = (3-level)*'-----'
		print('\n' + indent, name, indent + '\n')
		f.write(str('\n' + indent + name + indent + '\n'))
		table_data = []
		table_text = []
		table = soup.find('table')
		if table:
			table_body = table.find('tbody')
			if table_body:
				rows = table_body.find_all('tr')
				if rows:
					titles = soup.find_all('p', {'class': (table['class'][0])[:-5]})
					for title in titles:
						b = BeautifulSoup(str(title), features='html.parser').find('b')
						if b:
							if b.contents:
								if str(b.contents[0])[0] != '<':
									title = b.contents[0]
									break
					for row in rows:
						cols = row.find_all('td')
						cols = [ele.text.strip() for ele in cols]
						table_data.append([ele for ele in cols if ele])
					if 'title' in vars() or 'title' in globals(): 
						print('\n', title, ':\n')
						f.write(str('\n' + title + ':\n'))
					for td in table_data:
						print(td)
						f.write(str(td))
						table_text += td
				else:
					table = soup.find_all('table')
					for t in table:
						titles = soup.find_all('p', {'class': (t['class'][0])[:-5]})
						for title in titles:
							b = BeautifulSoup(str(title), features='html.parser').find('b')
							if b:
								if b.contents:
									if str(b.contents[0])[0] != '<':
										title = b.contents[0]
										break
						table_body = t.find('tbody')
						if table_body:
							rows = table_body.find_all('tr')
							if rows:
								for row in rows:
									cols = row.find_all('td')
									cols = [ele.text.strip() for ele in cols]
									table_data.append([ele for ele in cols if ele])
								print('\n', title, ':\n')
								f.write(str('\n' + title + ':\n'))
								for td in table_data:
									print(td)
									f.write(str(td))
									table_text += td
		text = soup.find_all('p')
		for t in text:
			if t.contents:
				word = str(t.contents[0])
				if word[0] != '<' and len(word.split(' ')) > 1:
					if word not in table_text and word[:18] != '[if !supportLists]':
						if 'strong>' in word:
							word = word.replace('<strong>', '').replace('</strong>', '')
						print(word)
						f.write(str(word))
			info = BeautifulSoup(str(t), features='html.parser').find('span')
			if info:
				if info.contents:
					word = str(info.contents[0])
					if word[0] != '<' and len(word.split(' ')) > 1:
						if word not in table_text and word[:18] != '[if !supportLists]':
							if 'strong>' in word:
								word = word.replace('<strong>', '').replace('</strong>', '')
							print(word)
							f.write(str(word))
			extra_link = BeautifulSoup(str(t), features='html.parser').find('a')
			if extra_link:
				if str(extra_link['href'])[:4] != '?uri=':
					if '.pdf' not in str(extra_link['href']).lower():
						parse_link(extra_link['href'], level+1)
	except Exception as ex:
		return

if __name__ == '__main__':
	r  = requests.get('https://nu.edu.kz/admissions')
	data = r.text
	soup = BeautifulSoup(data, features='html.parser')
	result = soup.find_all('li', {'class': 'menu-item'})
	result = ''.join(str(result))
	soup = BeautifulSoup(result, features='html.parser')
	result = soup.find_all('a', href=True)
	for a in result:
		print('\n---------------', a.contents[0], '---------------\n')
		f.write(str('\n---------------' + a.contents[0] + '---------------\n'))
		link = a['href']
		if link[-4:] != '.pdf':
			try:
				r = requests.get(link)
				data = r.text
				soup = BeautifulSoup(data, features='html.parser')
				text = soup.find_all('p')
				for i in text:
					if i.contents:
						word = str(i.contents[0])
						if word[0] != '<' and len(word.split(' ')) > 1:
							if 'strong>' in word:
								word = word.replace('<strong>', '').replace('</strong>', '')
							print(word)
							f.write(word)
				subresult = soup.find_all('li', {'class': 'wpthemeNavListItem wpthemeLeft'})
				for i in subresult:
					soup = BeautifulSoup(str(i), features='html.parser')
					name = soup.find('span').contents[0]
					link = soup.find_all('a', href=True)
					for l in link:
						parse_link(l['href'], 1)
			except Exception as ex:
				# print(ex)
				continue