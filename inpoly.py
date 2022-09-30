'''testing for being inside a polynomial.  Two cases: Convex and general
You are not responsible for understanding the geometric code!
'''

from graphics import *
import math

def pointsToTuples(pointList):
    '''Given a list of graphics Points,
    return a list of the coordinates as tuples:
    [(x1, y1), (x2, y2), ...]
    These are used forinside-outside calculation functions
    and convexity testing in this module.'''
    tups = []
    for pt in pointList:
        tups.append((pt.getX(), pt.getY()))
    return tups

def insideConvexPoly(pt, coordsClockwise):
    '''True if Point pt is inside the CONVEX polygon whose vertex
    coordinate tuples are listed in clockwise order in coordsClockwise.
    This often runs faster than the general algorithm in insidePoly.'''

    #Algorithm:
    #  Tests if pt is to the right of each line from one vertex to the next

    if len(coordsClockwise) < 3:
        return False
    px = pt.getX()
    py = pt.getY()
    lastx, lasty = coordsClockwise[-1] # is before the first listed point
    for x, y in coordsClockwise:
        if (px-lastx)*(y-lasty) <= (py-lasty)*(x-lastx):
            return False
        lastx = x
        lasty = y
    return True

def insidePoly(pt, coordsClockwise):
    '''True if graphics Point pt is inside the polygon whose vertex
    coordinate tuples are listed in clockwise order in coordsClockwise.
    The polygon does not need to be convex.'''

    #Algorithm:
    #  add up the angle between successive rays from pt to the vertices:
    #  It is 2*pi if inside, 0 if outside
    #  angles easiest calculated via complex arithmetic (y coord imaginary)
    #  False immediately if it find pt at a vertex or on an edge.
    
    pz = complex(pt.getX(), pt.getY())
    zl = complex(*coordsClockwise[-1]) - pz
    angleSum = 0
    for x, y in coordsClockwise:
        if zl == 0:
            return False # pt is vertex
        z = complex(x, y) - pz
        q = z/zl
        if q.imag == 0 and q.real < 0:
            return False # negative ratio means pt on this edge
        angleSum -= math.atan2(q.imag, q.real) # ccw is positive
        zl = z
    #print('Windings:', angleSum/math.tau)  # debug = should be close to 0 or 1
    return angleSum > math.pi # should be 0 (outside) or 2*pi (inside)


def isConvex(coordsClockwise):
    '''True if polygon, 
    whose vertex coordinates tuples are listed in clockwise order
    in coordsClockwise, is convex.
    '''
    
    #Algorithm:
    #  Tests if successive edge turn right

    lastx, lasty = coordsClockwise[-2]
    midx, midy = coordsClockwise[-1]
    for x, y in coordsClockwise:
        if (midx-lastx)*(y-midy) > (midy-lasty)*(x-midx):
            return False
        lastx = midx
        lasty = midy
        midx = x
        midy = y
    return True

def dot(pt, win, color='black', r=3):
    '''draws filled circle pf specified color and radius
    and returns it.  No fill if color is None'''
    c = Circle(pt, r)
    if color != None:
        c.setFill(color)
    c.draw(win)
    return c
 
def testInside(poly, pts, win):
    '''draw polygon poly and points in list of Points, pts,
    showing whether they are inside (green) or outside (red), and
    for convex polygons: yellow if the two algorithms disagree.
    (They should not disagree!)
    '''
    tups = pointsToTuples(poly.getPoints())
    convex = isConvex(tups)
    print('Is convex:', convex)
    poly.draw(win)
    for pt in  pts:
        inside = insidePoly(pt, tups)
        if inside:
            color = 'green'
        else:
            color = 'red'
        if convex and (inside != insideConvexPoly(pt, tups)):
            color = 'yellow' # algorithm disagreement
        dot(pt, win, color=color)

def testing():

    win = GraphWin('Inside-Outside', 700, 700)
    win.yUp()
    # data copied from output of makePolyVertList.py
    poly = Polygon( [Point(135.0, 163.0), Point(190.0, 140.0),
                     Point(106.0, 121.0), Point(186.0, 107.0),
                     Point(114.0, 103.0), Point(159.0, 54.0),
                     Point(113.0, 80.0), Point(98.0, 58.0),
                     Point(31.0, 131.0), Point(147.0, 145.0),
                     Point(59.0, 173.0) ])
    testpts = [ Point(134.0, 157.0), Point(132.0, 137.0),
                Point(51.00, 125.0), Point(96.0, 77.0),
                Point(96.0, 110.0), Point(109.0, 151.0),
                Point(150.0, 125.0), Point(0, 90.0),
                Point(112.0, 65.0), Point(74.0, 153.0)] 
    testInside(poly, testpts, win)
    
    poly2 = Polygon([Point(281.0, 524.0),
                    Point(340.0, 553.0), Point(374.0, 537.0),
                    Point(396.0, 500.0), Point(399.0, 465.0),
                    Point(393.0, 454.0), Point(319.0, 442.0),
                    Point(292.0, 449.0), Point(268.0, 477.0),
                    Point(269.0, 505.0)])
    testpts2 = [Point(339.0, 545.0), Point(387.0, 483.0),
                Point(340.0, 456.0), Point(297.0, 457.0),
                Point(285.0, 492.0),Point(412.0, 478.0),
                Point(394.0, 523.0),Point(285.0, 594.0),
                Point(256.0, 495.0) ]
    testInside(poly2, testpts2, win)

    polyDegen = Polygon([Point(5, 5), Point(50, 50)]) # 2 points!
    
    testpts3 = [Point(10, 60), Point(50, 50), Point(40, 40)]

    # You should not be using a degenerate polygon (2 vertices)
    #   but the test does work
    testInside(polyDegen, testpts3, win)
  
testing() # if you delete this line, you can import this module and use it

    
