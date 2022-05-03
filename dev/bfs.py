graph = {
  'A' : ['B','C'],
  'B' : ['D', 'E'],
  'C' : ['F'],
  'D' : [],
  'E' : ['F'],
  'F' : []
}

visited = [] # List to keep track of visited nodes.
queue = []     #Initialize a queue


# Function to print a BFS of graph
def BFS(G, s):
	# Mark all the vertices as not visited
	visited = [False] * (max(G) + 1)
	# Create a queue for BFS
	queue = []

	# Mark the source node as
	# visited and enqueue it
	queue.append(s)
	visited[s] = True

	while queue:

		# Dequeue a vertex from
		# queue and print it
		s = queue.pop(0)
		print(s, end=" ")

		# Get all adjacent vertices of the
		# dequeued vertex s. If a adjacent
		# has not been visited, then mark it
		# visited and enqueue it
		for i in G[s]:
			if visited[i] == False:
				queue.append(i)
				visited[i] = True


def bfs(visited, graph, node):
  visited.append(node)
  queue.append(node)
  while queue:
    print('visited:', visited)
    print('queue:', queue)
    s = queue.pop(0)
    print('s:', s)
    for neighbour in graph[s]:
      print('neighbour:', neighbour)
      if neighbour not in visited:
        visited.append(neighbour)
        queue.append(neighbour)

# Driver Code
bfs(visited, graph, 'A')