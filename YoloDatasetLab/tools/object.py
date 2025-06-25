class Object:
    """
    Estimated object skeleton
    inputs:
        :x1,y1,x2,y2: top left and bottom right coordinates of object, can be float or int according to normalized param
        :label: numerical label, must be integer
        :normalized: when this param True, represents 0-1 float coordinates without absolute image width and height. when is False, represent 0-shape integer 
        coordinates with image width and image height ,default value is True"""
    
    __slots__ = [
        "x1", "y1", "x2", "y2", "label", "normalized",
        "image_width", "image_height",
    ]
    
    def __init__(self,x1,y1,x2,y2,label:int,normalized:bool=True,image_width=None,image_height=None,):
        
        assert isinstance(label,int), "Label must be integer"
        assert x1 < x2, "x1 coordinate must be lower than x2"
        assert y1 < y2, "y1 coordinate must be lower than y2"
        
        if normalized:
            assert all(isinstance(coord, float) for coord in [x1, x2, y1, y2]), "Coordinate must be float when normalized param = True"
            assert all(0 <= coord <= 1 for coord in [x1,x2,y1,y2]), f"Coordinate must be between 0 and 1 when normalized param = True {x1} {x2} {y1} {y2}"
        else:
            assert all(isinstance(coord, int) for coord in [x1, x2, y1, y2]), "Coordinate must be int when normalized param = False"
            assert image_height != None and image_width != None, "image_height or image_width must be given when normalized param = False" 
            assert all(0 <= coord <= image_width for coord in [x1,x2]), f"x values must be between 0 and image_width, current: x1:{x1},x2:{x2} image_width:{image_width}"
            assert all(0 <= coord <= image_height for coord in [y1,y2]), f"y values must be between 0 and image_height current: y1:{y1},y2:{y2} image_heigh:{image_height}"
            assert isinstance(image_height,int) and isinstance(image_width,int), f"image width and image height must be integer when normalized param = False, current: {image_width} {image_height}"
       
        self.label = label
        self.normalized = normalized
        self.x1,self.y1,self.x2,self.y2 = x1,y1,x2,y2
        self.image_width,self.image_height = image_width,image_height
        
        
    def __repr__(self):
        return f"Object(x1,y1:({self.x1},{self.y1}) x2,y2:({self.x2},{self.y2}) lbl:{self.label} norm:{self.normalized} )"
    
    def to_absolute(self,image_width:int,image_height:int):
        """
        Convert object to absolute coordinates
        """
        assert self.normalized == True,"Object already absolute"
        assert isinstance(image_width,int) and isinstance(image_height,int),"image_width and image_height must be integer"
        self.x1 = int(self.x1 * image_width)
        self.x2 = int(self.x2 * image_width)
        self.y1 = int(self.y1 * image_height)
        self.y2 = int(self.y2 * image_height)
        self.normalized = not self.normalized
        self.image_height = image_height
        self.image_width = image_width
        
    def to_normalized(self):
        """
        Convert object to normalized coordinates
        warning: this process converts old image_width and image_height to None value
        """
        assert self.normalized == False,"Object already normalized"
        self.x1 = float(self.x1 / self.image_width)
        self.x2 = float(self.x2 / self.image_width)
        self.y1 = float(self.y1 / self.image_height)
        self.y2 = float(self.y2 / self.image_height)
        self.normalized = not self.normalized
        self.image_width = None
        self.image_height = None        
        
    @property
    def topleft(self):
        """
        returns top eft coordinates like tuple(x,y)
        """
        return (self.x1,self.y1)
    
    @property
    def topright(self):
        """
        returns top right coordinates like tuple(x,y)
        """
        return (self.x2,self.y1)

    @property
    def bottomleft(self):
        """
        returns bottom left coordinates like tuple(x,y)
        """
        return (self.x1,self.y2)
    
    @property
    def bottomright(self):
        """
        returns bottom right coordinates like tuple(x,y)
        """
        return (self.x2,self.y2)
        
    @property
    def center(self):
        """
        returns center point coordinates like tuple(x,y)
        """
        x = (self.x1 + self.x2) / 2
        y = (self.y1 + self.y2) / 2
        
        if self.normalized:
            return (x,y)
        else:
            return(int(x),int(y))
        
    @property
    def width(self):
        """
        returns width
        """
        return self.x2-self.x1
    
    @property
    def height(self):
        """
        returns height
        """
        return self.y2-self.y1
    
    @property
    def area(self):
        """
        returns area value
        """
        w = self.width
        h = self.height
        return h*w
        
    @classmethod
    def fromStringXYXYF(cls,string):
        """
        Build Object from text, text format: ratio coordinates: 'label x1 y1 x2 y2' , 'int float float float float'
        example:
            Object.fromStringXXYF("1 0.4 0.2 0.6 0.5")
        inputs:
            text
        returns:
            Object
        """
        if string[-2:] == '\\n':
            string = string[-2:]
        parts = string.split(" ")
        assert len(parts) == 5 , "length of elements not equal to 5"
        try:
            lbl = int(parts[0])
            x1,y1,x2,y2 = map(float,parts[1:])
        except Exception as e :
            raise ValueError(f"{e}")
        return cls(x1,y1,x2,y2,lbl,True)
    
    @classmethod
    def fromStringXYXYI(cls,string,image_width,image_height):
        """
        Build Object from text, text format: absolute coordinates : 'label x1 y1 x2 y2' , 'int int int int int'
        example:
            Object.fromStringXXYF("1 522 500 12 234")
        inputs:
            text
        returns:
            Object
        """
        if string[-2:] == '\\n':
            string = string[-2:]
        parts = string.split(" ")
        assert len(parts) == 5 , "length of elements not equal to 5"
        try:
            lbl = int(parts[0])
            x1,y1,x2,y2 = map(int,parts[1:])
        except Exception as e :
            raise ValueError(f"{e}")
        return cls(x1,y1,x2,y2,lbl,False,image_width,image_height)
    
    @classmethod
    def fromStringXYWHF(cls,string):
        """
        Build Object from text, text format: ratio coordinates : 'label center_x center_y width height' , 'int float float float float'
        example:
            Object.fromStringXXYF("1 0.4 0.4 0.2 0.2")
        inputs:
            text
        returns:
            Object
        """
        if string[-2:] == '\\n':
            string = string[-2:]
        parts = string.split(" ")
        assert len(parts) == 5 , "length of elements not equal to 5"
        try:
            lbl = int(parts[0])
            x,y,w,h = map(float,parts[1:])
        except Exception as e :
            raise ValueError(f"{e}")
        
        x1 = float(x - w / 2)
        x2 = float(x + w / 2)
        y1 = float(y - h / 2)
        y2 = float(y + h / 2)
        
        
        x1 = float(max(0, min(1, x1)))
        y1 = float(max(0, min(1, y1)))
        x2 = float(max(0, min(1, x2)))
        y2 = float(max(0, min(1, y2)))
       
        return cls(x1,y1,x2,y2,lbl,True)

    @classmethod
    def fromStringXYWHI(cls,string,image_width,image_height):
        """
        Build Object from text, text format: absolute coordinates : 'label center_x center_y width height' , 'int int int int int'
        example:
            Object.fromStringXXYF("1 522 500 12 120")
        inputs:
            text
        returns:
            Object
        """
        if string[-2:] == '\\n':
            string = string[-2:]
        parts = string.split(" ")
        assert len(parts) == 5 , "length of elements not equal to 5"
        try:
            lbl = int(parts[0])
            x,y,w,h = map(int,parts[1:])
        except Exception as e :
            raise ValueError(f"{e}")
        x1 = x - int(w/2)
        x2 = x + int(w/2)
        y1 = y - int(h/2)
        y2 = y + int(h/2)
        return cls(x1,y1,x2,y2,lbl,False,image_width,image_height)
        
    def contains(self, x, y)->bool:
        """
        Checks if the given (x, y) point is inside the object bounding box.
        return: result with bool type
        """
        if self.normalized:
            assert 0 <= x <= 1 and 0 <= y <= 1, "Coordinates must be between 0 and 1 when normalized"
        else:
            assert self.image_width is not None and self.image_height is not None, "Image dimensions must be set for absolute coordinates"
            assert 0 <= x <= self.image_width and 0 <= y <= self.image_height, "Coordinates must be within image bounds"
        
        return self.x1 <= x <= self.x2 and self.y1 <= y <= self.y2
    
    def touches_boundary(self,tolerance_interval=0)->bool:
        """
        Checks if the object touches the image edges.
        
        :param tolerance_interval: Defines a buffer zone from the edges (default: 0).
        :return: True if the object touches any edge, False otherwise.
        """
        if self.x1 <= 0 + tolerance_interval or self.x1 >= self.image_width - tolerance_interval:
            return True
        elif self.y1 <= 0 + tolerance_interval or self.y1 >= self.image_height - tolerance_interval:
            return True
        elif self.x2 <= 0 + tolerance_interval or self.x2 >= self.image_width - tolerance_interval:
            return True
        elif self.y2 <= 0 + tolerance_interval or self.y2 >= self.image_height - tolerance_interval:
            return True
        else:
            return False
        
    def intersects(self,other):
        """
        Checks if the object intersects with another object.
        
        :param other: Another Object instance.
        :return: True if any corner of 'other' is inside 'self', otherwise False.
        """

        result = False
        for x,y in [other.topleft,other.topright,other.bottomright,other.bottomleft]:
            if self.contains(x,y):
                result = True 
                break
        
        return  result
       
    def get_XYWHF_string(self):
        """
        Returns a string in YOLO format: 'label center_x center_y width height' with floats (normalized).
        """
        assert self.normalized, "Object must be normalized to use to_XYWHF_string"
        center_x = (self.x1 + self.x2) / 2
        center_y = (self.y1 + self.y2) / 2
        width = self.x2 - self.x1
        height = self.y2 - self.y1
        return f"{self.label} {center_x} {center_y} {width} {height}"
    
    @staticmethod 
    def XYXY_to_XYWH(text:str,type='f')->str:
        """
        Convert annotiation to 'L CENTER_X CENTER_Y W H' from 'L X1 Y1 X2 Y2'
        inputs:
            text:'L X1 Y1 X2 Y2'
            type: must be 'f' or 'i', f for normalized, i for absolute coordinates
        """
        if type == 'f':
            try:
                l,x1,y1,x2,y2 = list(map(lambda x: float(x),text.split(" ")))   
            except:
                raise Exception('Text must contain 5 element and elements must be float')
            center_x = (x1 + x2) / 2 
            center_y = (y1 + y2) / 2
            width = x2-x1
            height = y2-y1
            
            return f"{int(l)} {center_x} {center_y} {width} {height}"    
        elif type == 'i':
            try:
                l,x1,y1,x2,y2 = list(map(lambda x: int(x),text.split(" ")))
            except:
                raise Exception('Text must contain 5 element and elements must be int')
            center_x = int((x1 + x2) / 2 )
            center_y = int((y1 + y2) / 2)
            width = x2-x1
            height = y2-y1
            
            return f"{int(l)} {center_x} {center_y} {width} {height}"    
        else:
            raise KeyError('Type argument must be f or i')
        

        
        
        
              
    
        
        
        
