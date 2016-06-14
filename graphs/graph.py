import networkx as nx
from networkx.readwrite import json_graph
import csv
import sys
import matplotlib.pyplot as plt
import json
import pickle
import statistics
import copy

def count_authors_and_papers(filename):
	
	num_papers = 0
	linelengths = []

	with open(filename, 'r') as f:
		for line in f:
			arrLine = line.split(",")
			count = 0
			for name in arrLine:
				count += 1
			linelengths.append(count)
			num_papers += 1

	m = max(linelengths)
	return [m, num_papers]

def convert_text_to_csv(filename, outfile):

	retval = count_authors_and_papers(filename)
	max_authors = retval[0]
	num_papers = retval[1]
	all_authors = [[] for x in range(max_authors)] 

	with open(filename, 'r') as f:
		for line in f:
			arrLine = line.split(",")
			position = 0
			for name in arrLine:
				name = name.strip('\n').strip('\t').lstrip().rstrip()
				all_authors[position].append(name)
				position += 1
			while position < max_authors:
				all_authors[position].append('')
				position += 1
	
	return write_csv(all_authors, outfile, max_authors, num_papers)

def write_csv(all_authors, csvfilename, max_authors, num_papers):

	first_row = ['First Author']
	for i in range(2, max_authors + 1):
		first_row.append(str(i))

	with open(csvfilename, 'wt', newline='') as csvf:
		writer = csv.writer(csvf)
		writer.writerow(first_row)
		for j in range(num_papers):
			row = []
			for i in range(max_authors): 
				row.append(all_authors[i][j])
			writer.writerow(row)
	return

def simple_stats(filename):

	authors = set()
	linelengths = []
	num_papers = 0
	# lastnames = set()
	# duplicates = set()

	with open(filename, 'r') as csvfile:
		reader = csv.reader(csvfile, delimiter=',')
		for row in reader:
			if row[0] == 'First Author':
				continue
			author_count = 0
			for i in range(len(row)):
				author_count += 1
				if row[i] == '':
					continue
				author = row[i].rstrip().lstrip()
				authors.add(author)
				# last_name = author.split(" ")
				# last_name = ' '.join(last_name[1:])
				# if last_name in lastnames:
				# 	duplicates.add(last_name)
				# else:
				# 	lastnames.add(last_name)
			
			linelengths.append(author_count)
			num_papers += 1
	m = max(linelengths)

	with open('simplestats.out', 'w') as f: 
		f.write('Max number of authors writing a single paper: ' + str(m) + '\n')
		f.write('Total unique number of authors: ' + str(len(authors)) + '\n')
		f.write('Total number of papers: ' + str(num_papers) + '\n')

	print(authors)
	print('Max number of authors writing a single paper: ' + str(m))
	print('Unique number of authors: ' + str(len(authors)))
	print('Number of papers: ' + str(num_papers))
	# print('Unique number of last names: ' + str(len(lastnames)))
	# print(duplicates)
	print('Done! This info has been saved to <simplestats.out>.')


#code to regenerate the authors.txt file after deleting it.
# f = open('finalauthors.txt', 'w+')
# with open('separated-authors.csv', 'r') as csvfile:
# 	reader = csv.reader(csvfile, delimiter=',')
# 	for row in reader:
# 		line = row[0]
# 		for i in range(1, 11):
# 			line = line + ', ' + row[i]
# 		print(line)
# 		f.write(line + '\n')
# f.close()

def read_from_csv(filename): 

	author_matrix = []
	author_nodes_set = set()

	#filtering out the nodes from csv
	with open(filename, 'r') as csvfile:
		reader = csv.reader(csvfile, delimiter=',')
		for row in reader:
			#skip the first row
			if 'First Author' in row:
				continue
			line = []
			for i in range(len(row)):
				if row[i] != '':
					line.append(row[i])
					author_nodes_set.add(row[i])
			author_matrix.append(line)

	return {'author_matrix': author_matrix, 'author_nodes': author_nodes_set}

def generate_author_to_int_dictionary(filename):

	retdict = read_from_csv(filename)
	author_nodes = retdict['author_nodes']
	author_matrix = retdict['author_matrix']

	#assigning each author an integer representation
	author_to_int, i = dict(), 0
	sorted_authors = sorted(author_nodes)

	for item in sorted_authors:
		author_to_int[item] = i
		i += 1

	#saving the author to int dictionary
	pickle.dump(author_to_int, open("author_int_dict.p", "wb"))
	pickle.dump(author_matrix, open("author_matrix.p", "wb"))

def generate_adj_matrix():

	author_to_int = pickle.load(open("author_int_dict.p", "rb"))
	author_matrix = pickle.load(open("author_matrix.p", "rb"))

	#initializing adjacency matrix
	size = len(author_to_int)
	M = [[0 for i in range(size)] for j in range(size)]

	#adding edges from each author
	for paper in range(len(author_matrix)):
		num_authors = len(author_matrix[paper])
		for j in range(num_authors):
			a1 = author_matrix[paper][j]
			for k in range(j + 1, num_authors):
				a2 = author_matrix[paper][k]
				M[author_to_int[a1]][author_to_int[a2]] = 1
				M[author_to_int[a2]][author_to_int[a1]] = 1

	pickle.dump(M, open("adjacency_matrix.p", "wb"))

	#save graph and dict info into a readable text file for debugging
	with open('adjacency_matrix.txt', 'w') as f: 
		f.write("Authors to Integers Dictionary \n")
		#listing authors by their values
		for item in sorted(author_to_int, key=author_to_int.get):
			f.write(str(item) + " : " + str(author_to_int[item]) + "\n")
		f.write("\n\n\nPure python matrix: \n\n")
		for row in M: 
			f.write(str(row).strip("]").strip("[") + "\n")

def generate_networkX_graph_int():

	global G
	G = nx.Graph()
	author_to_int = pickle.load(open("author_int_dict.p", "rb"))
	matrix = pickle.load(open("adjacency_matrix.p", "rb"))

	#adding each int to the graph G
	for key in author_to_int: 
		G.add_node(author_to_int[key])

	s = len(matrix)
	for i in range(s):
		for j in range(s):
			if matrix[i][j] == 1:
				G.add_edge(i, j)

def generate_networkX_graph_string():

	global G
	G = nx.Graph()
	author_to_int = pickle.load(open("author_int_dict.p", "rb"))
	author_matrix = pickle.load(open("author_matrix.p", "rb"))

	#adding each author's name to the graph G
	for key in author_to_int: 
		G.add_node(key)

	num_papers = len(author_matrix)
	for row in range(num_papers):
		num_authors = len(author_matrix[row])
		for j in range(num_authors):
			a1 = author_matrix[row][j]
			for k in range(j + 1, num_authors):
				a2 = author_matrix[row][k]
				G.add_edge(a1, a2)

def write_json(type):

	if type == 'int':
		with open('data_int.json', 'w') as outfile1:
			outfile1.write(json.dumps(json_graph.node_link_data(G)))
		print('Dumped into file <data_int.json>.')

	elif type == 'string':
		with open('data_string.json', 'w') as outfile1:
			outfile1.write(json.dumps(json_graph.node_link_data(G)))
		print('Dumped into file <data_string.json>.')

def nx_draw_graph():

	plt.figure(figsize=(8,8))
	plt.xlim(-0.05,1.05)
	plt.ylim(-0.05,1.05)
	plt.axis('off')
	nx.draw(G)
	plt.savefig('graph_new.png')
	plt.show()

def calculate_metrics():

	# author_to_int = pickle.load(open("author_int_dict.p", "rb"))
	# matrix = pickle.load(open("adjacency_matrix.p", "rb"))
	# author_matrix = pickle.load(open("author_matrix.p", "rb"))
	# papers_per_author(author_matrix)
	# authors_per_paper(author_matrix)
	# density(matrix)
	# author_degrees(matrix, author_to_int)

	# connected_components(matrix, author_to_int)
	# cut_point(author_to_int)

	# clustering_coefficient()
	# betweenness_centrality()
	closeness_centrality()

	# print(diameter(matrix))

def betweenness_centrality():

	generate_networkX_graph_string()
	between = nx.betweenness_centrality(G)
	sorted_between = sorted(between, key=between.get)
	stats = [between[key] for key in sorted_between]

	average = statistics.mean(stats)
	median = statistics.median(stats)
	median_low = statistics.median_low(stats)
	median_high = statistics.median_high(stats)
	mode = statistics.mode(stats)

	with open('betweenness_centrality.txt', 'w') as f: 
		for author in sorted_between:
			f.write(author + ": " + str(between[author]) + '\n')
		f.write('\nAverage: ' + str(average) + '\n')
		f.write('Median: ' + str(median) + '\n')
		f.write('Median low: ' + str(median_low) + '\n')
		f.write('Median high: ' + str(median_high) + '\n')
		f.write('Mode: ' + str(median_high) + '\n')	

	print("Average betweenness is: " + str(average))
	# 6.894441787211672e-05			

def clustering_coefficient():

	generate_networkX_graph_string()
	coeff = nx.clustering(G)
	sorted_coeff = sorted(coeff, key=coeff.get)
	stats = [coeff[key] for key in sorted_coeff]

	average = statistics.mean(stats)
	median = statistics.median(stats)
	median_low = statistics.median_low(stats)
	median_high = statistics.median_high(stats)
	mode = statistics.mode(stats)

	with open('clustering_coefficient.txt', 'w') as f: 
		for author in sorted_coeff:
			f.write(author + ": " + str(coeff[author]) + '\n')
		f.write('\nAverage: ' + str(average) + '\n')
		f.write('Median: ' + str(median) + '\n')
		f.write('Median low: ' + str(median_low) + '\n')
		f.write('Median high: ' + str(median_high) + '\n')
		f.write('Mode: ' + str(median_high) + '\n')	

	print ("Average clustering is: " + " " + str(average))
	#clustering coefficient : 0.8099788585502871

def closeness_centrality():

	generate_networkX_graph_string()
	closeness = nx.closeness_centrality(G)
	sorted_closeness = sorted(closeness, key=closeness.get)
	stats = [closeness[key] for key in sorted_closeness]

	average = statistics.mean(stats)
	median = statistics.median(stats)
	median_low = statistics.median_low(stats)
	median_high = statistics.median_high(stats)
	mode = statistics.mode(stats)

	with open('closeness_centrality.txt', 'w') as f: 
		for author in sorted_closeness:
			f.write(author + ": " + str(closeness[author]) + '\n')
		f.write('\nAverage: ' + str(average) + '\n')
		f.write('Median: ' + str(median) + '\n')
		f.write('Median low: ' + str(median_low) + '\n')
		f.write('Median high: ' + str(median_high) + '\n')
		f.write('Mode: ' + str(median_high) + '\n')	

	print ("Average closeness is: " + " " + str(average))
	# 0.02251066871887446
	
def diameter(matrix):
	
	v = len(matrix)
	dist = [[] for x in range(v)]
	for k in range(v):
		for i in range(v):
			for j in range(v):
				dist = min(dist[i][j], dist[i][k] + dist[k][j])
	return dist

def cut_point(author_to_int): 

	adj_list = pickle.load(open("adj_list.p", "rb"))
	list_of_ints = pickle.load(open("list_of_ints.p", "rb"))
	final = set()

	for cc in list_of_ints:
		if len(cc) <= 4:
			continue
		cc = sorted(cc)
		#graph contains only the connected component
		print("Connected component: " + str(cc))
		cut_points = find_cut_points_in_cc(adj_list, cc)
		if not cut_points:
			print("There are no cut points.")
		else: 
			print("Cut points: " + str(cut_points))
			new_cut_points = filter_cut_points(adj_list, cut_points, cc)
			if not new_cut_points:
				print("All filtered out. \n")
			elif new_cut_points == cut_points:
				print("No need to filter. \n")
			else: 
				print("Filtered cut points: " + str(new_cut_points) + "\n")
		final = final.union(new_cut_points)

	inverse_author_dict = {v: k for k, v in author_to_int.items()}
	translated = [inverse_author_dict[int] for int in author_to_int]

	print("Cut points for all ccs: " + str(translated))

def find_cut_points_in_cc(graph, cc):

	v = len(graph)
	visited, prev = [False for _ in range(v)], [None for _ in range(v)]
	discover, low = [0 for _ in range(v)], [0 for _ in range(v)]
	cut_points = set()

	def cut_dfs(start):

		visited[start] = True
		nonlocal time
		time += 1
		low[start] = discover[start] = time
		for w in graph[start]:
			if not visited[w]:
				prev[w] = start
				cut_dfs(w)
				low[start] = min(low[start], low[w])
			elif w != prev[start]: 
				#then w is visited, and (start, w) must be a back edge
				low[start] = min(low[start], discover[w]) 

	for vertex in cc:
		if not visited[vertex]:
			time = 0
			cut_dfs(vertex)
		break

	for vertex in cc:
		if prev[vertex] == None:
			if len(graph[vertex]) > 1:
				cut_points.add(vertex)
		else:
			for w in graph[vertex]:
				if low[w] >= discover[vertex]:
					cut_points.add(vertex)
	return cut_points

def filter_cut_points(graph, cut_points, cc):

	v = len(graph)
	filtered_cut_points = set()

	for cut in cut_points:
		new_graph = copy.deepcopy(graph)
		for edge in new_graph: 
			if cut in edge: 
				edge.remove(cut)
		metavisited, small_ccs = [False for _ in range(v)], []
		for vertex in cc:
			if vertex != cut and not metavisited[vertex]:
				ret = dfs(metavisited, vertex, new_graph)
				small_ccs.append(ret[0])
				metavisited = ret[1]
		if len(small_ccs) >= 2:
			filtered_cut_points.add(cut)
		print("Cut vertex: " + str(cut))
		print(str(small_ccs))

	return filtered_cut_points

def dfs(metavisited, start, graph):

	visited, stack = set(), [start]
	while stack:
		vertex = stack.pop()
		if vertex not in visited: 
			metavisited[vertex] = True
			visited.add(vertex)
			stack.extend(graph[vertex] - visited)
	return [visited, metavisited]
	
def connected_components(matrix, author_to_int):

	#convert matrix to adj_list
	v = len(matrix)
	adj_list = convert_matrix_to_adj_list(matrix, v)

	#using dfs to find connected components
	metavisited, list_of_ints = [False for _ in range(v)], []

	for vertex in range(v):
		if not metavisited[vertex]:
			ret = dfs(metavisited, vertex, adj_list)
			list_of_ints.append(ret[0])
			metavisited = ret[1]

	largest = largest_connected(list_of_ints)
	max_cc_size, max_cc, sizes = largest[0], largest[1], sorted(largest[2])

	#convert components of ints into authors
	inverse_author_dict = {v: k for k, v in author_to_int.items()}
	list_of_strings, max_cc_string = [], []
	
	for cc in list_of_ints:
		string_cc = [inverse_author_dict[i] for i in cc]
		if cc == max_cc:
			max_cc_string = string_cc
		list_of_strings.append(string_cc)

	#statistics of cc sizes
	average = statistics.mean(sizes)
	median = statistics.median(sizes)
	median_low = statistics.median_low(sizes)
	median_high = statistics.median_high(sizes)
	mode = statistics.mode(sizes)

	#saving info into a text file
	with open('connected_components.txt', 'w') as f: 
		f.write('Connected authors: ' + '\n')
		for cc in list_of_strings:
			f.write(str(len(cc)) + '   ' + str(cc) + '\n')
		f.write('\n')
		f.write('Connected nodes: ' + '\n')
		for cc in list_of_ints:
			f.write(str(len(cc)) + '   ' + str(cc) + '\n')
		f.write('\n')
		f.write('Number of connected components: ' + str(len(list_of_ints)) + '\n')
		f.write('Largest component size: ' + str(max_cc_size) + '\n')
		f.write('Largest connected component: ' + str(max_cc_string) + '\n')
		f.write('Component sizes: ' + str(sizes) + '\n')
		f.write('Average component size: ' + str(average) + '\n')
		f.write('Median: ' + str(median) + '\n')
		f.write('Low median: ' + str(median_low) + '\n')
		f.write('High median: ' + str(median_high) + '\n')
		f.write('Mode: ' + str(mode))

	pickle.dump(adj_list, open("adj_list.p", "wb"))
	pickle.dump(list_of_ints, open("list_of_ints.p", "wb"))

def convert_matrix_to_adj_list(matrix, size):

	adj_list = []
	for i in range(size):
		neighbors = set()
		for j in range(size): 
			if matrix[i][j] == 1:
				neighbors.add(j)
		adj_list.append(neighbors)
	return adj_list

def largest_connected(list_of_ints):

	sizes, s = dict(), []
	for list in list_of_ints:
		i = len(list) 
		sizes[i] = list
		s.append(i)
	m = max(sizes.keys())
	return [m, sizes[m], s]

def density(matrix):

	e = 0
	v = len(matrix)
	for i in range(v):
		for j in range(v): 
			if matrix[i][j] == 1:
				e += 1
	d = (2*e) / (v*(v-1))
	print(d)
	# d = 0.03507826763640717

def author_degrees(matrix, author_to_int):

	stats = dict()
	v = len(matrix)
	sorted_authors = sorted(author_to_int, key=author_to_int.get)
	for key in sorted_authors:
		stats[key] = 0
	for i in range(v):
		for j in range(v): 
			if matrix[i][j] == 1:
				stats[sorted_authors[i]] += 1

	with open('author_degrees.csv', 'wt', newline='') as csvf:
		writer = csv.writer(csvf)
		writer.writerow(['Author', 'Degrees'])
		for key in sorted(stats, key=stats.get):
			writer.writerow([key, str(stats[key])])

def papers_per_author(author_matrix):

	stats = dict()
	for row in author_matrix:
		for author in row:
			if author in stats:
				stats[author] += 1
			else: 
				stats[author] = 1 

	with open('papers_per_author.csv', 'wt', newline='') as csvf:
		writer = csv.writer(csvf)
		writer.writerow(['Author', 'Number of Papers'])
		for key in sorted(stats, key=stats.get):
			writer.writerow([key, str(stats[key])])

def authors_per_paper(author_matrix):

	linelengths = [len(paper) for paper in author_matrix]	
	with open('authors_per_paper.csv', 'wt', newline='') as csvf:
		writer = csv.writer(csvf)
		writer.writerow(['Paper', 'Number of Authors'])
		for i in range(len(linelengths)):
			writer.writerow([str(i), str(linelengths[i])])

def main():

	#input: python graph.py <input.txt> <csvfile>
	# text_file, csv_file = sys.argv[1], sys.argv[2]
	# convert_text_to_csv(text_file, csv_file)
	# simple_stats(csv_file)

	# print("Now generating json graph information...")
	#if dict and matrix pickle files already exist, do not execute the below lines
	# generate_author_to_int_dictionary(csv_file)
	# generate_adj_matrix()

	# generate_networkX_graph_string()
	# write_json(string)

	# generate_networkX_graph_int()
	# write_json(int)

	calculate_metrics()

	return "Finished"
                
if __name__ == "__main__":
    main()