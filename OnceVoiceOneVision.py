#Author-Leo
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback
import math, csv
import os.path, sys
from random import randint


def Merge_Bodies(rootComp):
    bodies = rootComp.bRepBodies
    combineFeatures = rootComp.features.combineFeatures    


    body = bodies.item(0)
    bodyCollection = adsk.core.ObjectCollection.create()
    i = 0
    for bod in bodies:
        if (i != 0):
            bodyCollection.add(bodies.item(i))
        i +=1
        
    combineFeatureInput = combineFeatures.createInput(body, bodyCollection)
    combineFeatureInput.operation = 0
    combineFeatureInput.isKeepToolBodies = False
    combineFeatureInput.isNewComponent = False
    returnValue = combineFeatures.add(combineFeatureInput)
    return returnValue

def move_camera(app, view, x,y,z, greatest_distance, fitview):
    try:
        if fitview:
            view.fit()
        #eye = camera.eye
        camera = view.camera
        
        target = adsk.core.Point3D.create(0,0,0)
        up = adsk.core.Vector3D.create(x,y,z)
        steps = 400
        
        #dist = camera.target.distanceTo(camera.eye)
        dist = greatest_distance*10
        for i in range(0, steps):
            eye = adsk.core.Point3D.create(10, dist * math.cos((math.pi*2) * (i/(2*steps) ) ),dist * math.sin((math.pi*2) * (i/(2*steps) )))
            
            camera.eye = eye
            camera.target = target
            camera.upVector = up
        
            camera.isSmoothTransition = False
            view.camera = camera
            adsk.doEvents()
            view.refresh()
    except:
        ui = app.userInterface
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))




def Circle(sketch,x,y,z,R):
    #draw a circle
    circles = sketch.sketchCurves.sketchCircles #get collection of circles
    circle = circles.addByCenterRadius (adsk.core.Point3D.create(x,y,z),R)

    #Get the profile defined by the circle
    prof = sketch.profiles.item(0)
    return prof

def Extrude(rootComp, prof, distance, symmetric):

    extrudes = rootComp.features.extrudeFeatures
    extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

    #Define extent of 5 cm
    extInput.setDistanceExtent(symmetric, adsk.core.ValueInput.createByReal(distance)) #symmetric? how deep we want to go

    ext = extrudes.add(extInput)
    return ext

def Axis (sketch,x0,y0,z0,x1,y1,z1):
    lines = sketch.sketchCurves.sketchLines
    axisLine = lines.addByTwoPoints(adsk.core.Point3D.create(x0, y0, z0), adsk.core.Point3D.create(x1, y1, z1))
    return axisLine

def Revolve (rootComp, prof,axis,Angle):
    revolves = rootComp.features.revolveFeatures
    revInput = revolves.createInput(prof, axis, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    #define angle revolve
    revInput.setAngleExtent(False,Angle)
    rev = revolves.add(revInput)
    return rev

def NewSketch(rootComp, plane):
    if plane == "top":
        sketch = rootComp.sketches.add(rootComp.xYConstructionPlane)
    if plane == "front":
        sketch = rootComp.sketches.add(rootComp.yZConstructionPlane)
    if plane == "right":
        sketch = rootComp.sketches.add(rootComp.xZConstructionPlane) 
    return sketch

def Sphere(rootComp,sketch,x,y,z,R):
    profCircle = Circle(sketch, x,y,z,R)
    axis = Axis(sketch, x-(R+1),y,z,x+(R+1),y,z)
    prof = sketch.profiles.item(0) #we get half sphere
    Angle = adsk.core.ValueInput.createByReal(2*math.pi)
    sphere = Revolve (rootComp, prof, axis, Angle)
    return sphere
 

def Rectangular_Pattern(ext,rootComp,Nx,dx,Ny,dy):
    #Get the body created by the extrusion
    body = ext.bodies.item(0)
    # Create input entities for rectangular pattern
    inputEntites = adsk.core.ObjectCollection.create()
    inputEntites.add(body)

    # Get x and y axes for rectangular pattern
    xAxis = rootComp.xConstructionAxis
    yAxis = rootComp.yConstructionAxis

    # Quantity and distance
    quantityOne = adsk.core.ValueInput.createByString(str(Nx))
    distanceOne = adsk.core.ValueInput.createByString(str(dx))
    quantityTwo = adsk.core.ValueInput.createByString(str(Ny))
    distanceTwo = adsk.core.ValueInput.createByString(str(dy))

    # Create the input for rectangular pattern
    rectangularPatterns = rootComp.features.rectangularPatternFeatures
    rectangularPatternInput = rectangularPatterns.createInput(inputEntites, xAxis, quantityOne, distanceOne, adsk.fusion.PatternDistanceType.SpacingPatternDistanceType)

    # Set the data for second direction
    rectangularPatternInput.setDirectionTwo(yAxis, quantityTwo, distanceTwo)

    # Create the rectangular pattern
    rectangularFeature = rectangularPatterns.add(rectangularPatternInput)

    return rectangularFeature

def Loft(rootComp,prof0, prof1):
    loftInput = rootComp.features.loftFeatures.createInput(adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    section1 = loftInput.loftSections.add(prof0)
    section2 = loftInput.loftSections.add(prof1)
    loft = rootComp.features.loftFeatures.add(loftInput)
    return loft

def Rectangle_top (sketch, x0,y0,z0,x1,y1): 
    lines = sketch.sketchCurves.sketchLines
    Line0 = lines.addByTwoPoints(adsk.core.Point3D.create(x0, y0, z0), adsk.core.Point3D.create(x1, y0, z0))
    Line1 = lines.addByTwoPoints(adsk.core.Point3D.create(x0, y0, z0), adsk.core.Point3D.create(x0, y1, z0))
    Line2 = lines.addByTwoPoints(adsk.core.Point3D.create(x1, y0, z0), adsk.core.Point3D.create(x1, y1, z0))
    Line3 = lines.addByTwoPoints(adsk.core.Point3D.create(x0, y1, z0), adsk.core.Point3D.create(x1, y1, z0))
    return sketch.profiles.item(0)

def Rectangle_front (sketch, x0,y0,z0,x1,z1):
    lines = sketch.sketchCurves.sketchLines
    Line0 = lines.addByTwoPoints(adsk.core.Point3D.create(x0, y0, z0), adsk.core.Point3D.create(x1, y0, z0))
    Line1 = lines.addByTwoPoints(adsk.core.Point3D.create(x0, y0, z0), adsk.core.Point3D.create(x0, y0, z1))
    Line2 = lines.addByTwoPoints(adsk.core.Point3D.create(x1, y0, z0), adsk.core.Point3D.create(x1, y0, z1))
    Line3 = lines.addByTwoPoints(adsk.core.Point3D.create(x0, y1, z0), adsk.core.Point3D.create(x1, y0, z1))
    return sketch.profiles.item(0)

def Rectangle_right (sketch, x0,y0,z0,y1,z1):
    lines = sketch.sketchCurves.sketchLines
    Line0 = lines.addByTwoPoints(adsk.core.Point3D.create(x0, y0, z0), adsk.core.Point3D.create(x0, y0, z1))
    Line1 = lines.addByTwoPoints(adsk.core.Point3D.create(x0, y0, z0), adsk.core.Point3D.create(x0, y1, z0))
    Line2 = lines.addByTwoPoints(adsk.core.Point3D.create(x0, y1, z0), adsk.core.Point3D.create(x0, y1, z1))
    Line3 = lines.addByTwoPoints(adsk.core.Point3D.create(x0, y1, z0), adsk.core.Point3D.create(x0, y0, z0))
    return sketch.profiles.item(0)


def LoadInstructions():
    Intructions_list = []
    with open('C:\\Users\\LEo\\Desktop\\HackHP2019\\instructions.csv','r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            Intructions_list.append(row)
    
    return Intructions_list


def Circular_Pattern(rootComp, ext,N):
    bodies = rootComp.bRepBodies
    combineFeatures = rootComp.features.combineFeatures    

    bodyCollection = adsk.core.ObjectCollection.create()
    bodyCollection.add(ext)


    ZAxis = rootComp.zConstructionAxis
    # Create the input for circular pattern
    circularFeats = rootComp.features.circularPatternFeatures
    circularFeatInput = circularFeats.createInput(bodyCollection, ZAxis)
    #Set the quantity of the elements
    circularFeatInput.quantity = adsk.core.ValueInput.createByReal(N)
    # Set the angle of the circular pattern
    circularFeatInput.totalAngle = adsk.core.ValueInput.createByString('360 deg')
    # Set symmetry of the circular pattern
    circularFeatInput.isSymmetric = False
    # Create the circular pattern
    circularFeat = circularFeats.add(circularFeatInput)
    return circularFeat


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        ui.messageBox('Hello script')
        design = app.activeProduct #give me what the the user is working on
        rootComp = design.rootComponent #Get the root component of the active design
        cur_sketch = NewSketch(rootComp, "top")

        Instructions = LoadInstructions()
        
        i = 0 
        greatest_dist = 0
        for inst in Instructions:
            if len(inst) > 0:
                if i != 0 : 
                    prof2 = prof
                if inst[0] == "Circle":
                    prof = Circle(cur_sketch, float (inst[2]),float(inst[3]), float(inst[4]), float(inst[1]))
                    i +=1
                    if greatest_dist < float(inst[1]):
                        greatest_dist = float(inst[1])
                elif inst[0] == "Extrude":
                    ext = Extrude(rootComp, prof2, float(inst[1]), bool(inst[2]))
                    prev_extrude =  True
                elif inst[0] == "Axis":
                    axis = Axis(cur_sketch, float(inst[1]), float(inst[2]),float(inst[3]), float(inst[4]),float(inst[5]), float(inst[6]))
                elif inst[0] == "Sphere":
                    sphere = Sphere(rootComp, cur_sketch, float(inst[2]), float(inst[3]), float(inst[3]), float(inst[1]))
                    if greatest_dist < float(inst[1]):
                        greatest_dist = float(inst[1])
                elif inst[0] == "Rectangle":
                    i +=1
                    if inst[1] == "xz":
                        prof = Rectangle_front(cur_sketch, float(inst[2]), float(inst[3]), float(inst[4]), float(inst[5]), float(inst[6]))
                        if abs(float(inst[2])- float(inst[5])) < abs(float(inst[4])- float(inst[6])):
                            if (abs(float(inst[4])- float(inst[6]))) >  greatest_dist:
                                greatest_dist = abs(float(inst[4])- float(inst[6]))
                        else:
                            if (abs(float(inst[2])- float(inst[5]))) >  greatest_dist:
                                greatest_dist = abs(float(inst[2])- float(inst[5]))
                    elif inst[1] == "yz":
                        prof = Rectangle_right(cur_sketch, float(inst[2]), float(inst[3]), float(inst[4]), float(inst[5]), float(inst[6]))
                        if abs(float(inst[3])- float(inst[5])) < abs(float(inst[4])- float(inst[6])):
                            if (abs(float(inst[4])- float(inst[6]))) >  greatest_dist:
                                greatest_dist = abs(float(inst[4])- float(inst[6]))
                        else:
                            if (abs(float(inst[3])- float(inst[5]))) >  greatest_dist:
                                greatest_dist = abs(float(inst[3])- float(inst[5]))
                    else:
                        prof = Rectangle_top(cur_sketch, float(inst[2]), float(inst[3]), float(inst[4]), float(inst[5]), float(inst[6]))
                        if abs(float(inst[2])- float(inst[5])) < abs(float(inst[3])- float(inst[6])):
                            if (abs(float(inst[3])- float(inst[6]))) >  greatest_dist:
                                greatest_dist = abs(float(inst[3])- float(inst[6]))
                        else:
                            if (abs(float(inst[2])- float(inst[5]))) >  greatest_dist:
                                greatest_dist = abs(float(inst[2])- float(inst[5]))    
                elif inst[0] == "NewSketch":
                    cur_sketch = NewSketch(rootComp, inst[1])
                elif inst[0] == "Revolve":
                    rev = Revolve (rootComp, prof,axis,float(inst[1]))
                elif inst[0] == "Loft":
                    loft = Loft (rootComp, prof, prof2)
                elif inst[0] == "Rectangular_Pattern":
                    if prev_extrude:
                        rect_pat = Rectangular_Pattern(ext,rootComp,int(inst[1]),float(inst[2]),int(inst[3]),float(inst[4]))
                        if (float(inst[1])*float(inst[2])) >  (float(inst[3])*float(inst[4])):
                            if (float(inst[1])*float(inst[2]))  >  greatest_dist:
                                greatest_dist = (float(inst[1])*float(inst[2]))
                        else:
                            if (float(inst[3])*float(inst[4]))  >  greatest_dist:
                                greatest_dist = (float(inst[3])*float(inst[4]))
                    else:
                        ui.messageBox('There was no previous extrude made, please first do a extrude then rectangular pattern')
                
            
      
        x = 0
        y = 0 
        z = 0
        R = 2 
        distance = 5
        cur_sketch = NewSketch(rootComp,"front")
        prof = Circle(cur_sketch,x,y,z,R)
        #move_camera(app, app.activeViewport, 0,0,1, greatest_dist, True)
        ext = Extrude(rootComp, prof, distance, False)
        #move_camera(app, app.activeViewport,0,0,1,greatest_dist, False)
        #rectangularFeature = Rectangular_Pattern(ext,rootComp, 5, 3, 3, 8) #Nx, dx, Ny, dy
        #move_camera(app, app.activeViewport,0,1,0,greatest_dist)


        #cur_sketch = NewSketch(rootComp,"xy")
        #x = 10
        #y = 10 
        #z = 10
        #R = 20
        #distance = 5
        #profCircle1 = Circle(cur_sketch,x,y,z,R)
        
        #cur_sketch = NewSketch(rootComp,"xy")
        #x = 20
        #y = 20 
        #z = 20
        #R = 5
        #distance = 5
        #profCircle2 = Circle(cur_sketch,x,y,z,R)
#        

        #Loft(rootComp, profCircle1, profCircle2) #works as long as we have two surfaces/objects

        #cur_sketch = NewSketch(rootComp,"xy")
        #sphere = Sphere(rootComp,cur_sketch, 0, 0, -10, 3)

        #x0 = 0 
        #y0 = 0
        #z0 = 5
        #x1 = 1
        #y1 = 2
        #cur_sketch = NewSketch(rootComp,"xy")
        #rectangle = Rectangle(cur_sketch, x0, y0, z0, x1, y1)
        #profCircle3 = Circle(cur_sketch,x0+5,y+5,z-2,R)
        #Loft(rootComp, rectangle, profCircle3) #works as long as we have two surfaces/objects
        
        
        #ext = Circular_Pattern(rootComp, ext, 5)
        

        bodies = rootComp.bRepBodies
        i = 0
        for bod in bodies:
            i +=1 
        if (i > 1):
            ext = Merge_Bodies(rootComp)

        #bodies = rootComp.bRepBodies
        #Rectangular_Pattern(ext, rootComp, 5, 100, 3, 100)
        #move_camera(app, app.activeViewport, 0,0,1, 1000, True)
        exportMgr = design.exportManager
        
        Dir = 'C:\\Users\\LEo\\Desktop\\HackHP2019'

        #stlOptions = exportMgr.createSTLExportOptions(Dir + '\\test.stl')
        #res = exportMgr.execute(sltOptions)

        stepOptions = exportMgr.createSTEPExportOptions(Dir+ '\\test.step')
        res = exportMgr.execute(stepOptions)


    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

