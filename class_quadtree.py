import pygame


class Quadtree:
	"""A Class implementing a quadtree."""
	def __init__(self, game, boundary, max_objects=4, depth=0):
		# boundary is a pg rect object with the very first rect being set in game class.
		self.game = game
		self.boundary = boundary
		self.max_objects = max_objects
		self.objects = []
		self.depth = depth
		self.divided = False

	def divide(self):
		"""Divide this node by spawning four children nodes."""
		cx, cy = self.boundary.centerx, self.boundary.centery
		w, h = self.boundary.width / 2, self.boundary.height / 2
		self.nw = Quadtree(self.game, pygame.Rect(cx - w, cy - h, w, h),
						   self.max_objects, self.depth + 1)
		self.ne = Quadtree(self.game, pygame.Rect(cx, cy - h, w, h),
						   self.max_objects, self.depth + 1)
		self.se = Quadtree(self.game, pygame.Rect(cx, cy, w, h),
						   self.max_objects, self.depth + 1)
		self.sw = Quadtree(self.game, pygame.Rect(cx - w, cy, w, h),
						   self.max_objects, self.depth + 1)
		self.divided = True

	def insert(self, object):
		"""Try to insert Point point into this QuadTree."""

		if not self.boundary.collidepoint(object.location):
			# The point does not lie inside boundary: bail.
			return False
		if len(self.objects) < self.max_objects:
			# There's room for our point without dividing the QuadTree.
			self.objects.append(object)
			return True

		# No room: divide if necessary, then try the sub-quads.
		if not self.divided:
			self.divide()

		return (self.ne.insert(object) or
				self.nw.insert(object) or
				self.se.insert(object) or
				self.sw.insert(object))

	def query(self, boundary, found_points):
		"""Find the points in the quadtree that lie within boundary."""

		if not pygame.Rect.colliderect(self.boundary, boundary):
			# If the domain of this node does not intersect the search
			# region, we don't need to look in it for points.
			return False

		# Search this node's points to see if they lie within boundary ...
		for i in self.objects:
			if pygame.Rect.colliderect(self.boundary, i.rect):
				found_points.append(i)
		# ... and if this node has children, search them too.
		if self.divided:
			self.nw.query(boundary, found_points)
			self.ne.query(boundary, found_points)
			self.se.query(boundary, found_points)
			self.sw.query(boundary, found_points)
		return found_points

	def __len__(self):
		"""Return the number of points in the quadtree."""

		n_points = len(self.points)
		if self.divided:
			n_points += len(self.nw) + len(self.ne) + len(self.se) + len(self.sw)
		return n_points

	def draw(self):
		"""Draw a representation of boundary to game screen."""

		pygame.draw.rect(self.game.screen, [100, 0, 0], self.boundary, 1)

		if self.divided:
			self.nw.draw()
			self.ne.draw()
			self.se.draw()
			self.sw.draw()

	# this is for querying in a radius but I have not made it compatible with pygame. #
	def query_circle(self, boundary, centre, radius, found_points):
		"""Find the points in the quadtree that lie within radius of centre.

		boundary is a Rect object (a square) that bounds the search circle.
		There is no need to call this method directly: use query_radius."""

		if not pygame.Rect.colliderect(self.boundary, boundary):
			# If the domain of this node does not intersect the search
			# region, we don't need to look in it for points.
			return False

		# Search this node's points to see if they lie within boundary
		# and also lie within a circle of given radius around the centre point.
		for i in self.objects:
			if (boundary.collidepoint(i.location) and
					i.location.distance_to(centre) <= radius):
				found_points.append(i)

		# Recurse the search into this node's children.
		if self.divided:
			self.nw.query_circle(boundary, centre, radius, found_points)
			self.ne.query_circle(boundary, centre, radius, found_points)
			self.se.query_circle(boundary, centre, radius, found_points)
			self.sw.query_circle(boundary, centre, radius, found_points)
		return found_points

	def query_radius(self, centre, radius, found_points):
		"""Find the points in the quadtree that lie within radius of centre."""

		# First find the square that bounds the search circle as a Rect object.
		boundary = pygame.Rect(*centre, 2 * radius, 2 * radius)
		return self.query_circle(boundary, centre, radius, found_points)

