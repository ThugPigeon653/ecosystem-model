class emotion():
    __mouth_type:float
    __pupil_size:float
    def __init__(self, mouth_type, pupil_size):
        self.__mouth_type=mouth_type
        self.__pupil_size=pupil_size

    def mouth_type(self)->float:
        return self.__mouth_type
    
    def pupil_size(self)->float:
        return self.__pupil_size
    
class creature():
    __eye_size:float
    __relative_strength:int
    __num_arms:int
    __leg_gap:float
    __default_emotion:emotion

    def __init__(self, eye_size, relative_strength, num_arms, leg_gap, default_emotion):
        self.__eye_size=eye_size
        self.__relative_strength=relative_strength
        self.__num_arms=num_arms
        self.__leg_gap=leg_gap
        self.__default_emotion=default_emotion

    def eye_size(self)->int:
        return self.__eye_size
    
    def relative_strength(self)->int:
        return self.__relative_strength
    
    def num_arms(self)->int:
        return self.__num_arms
    
    def leg_gap(self)->float:
        return self.__leg_gap
    
    def default_emotion(self)->emotion:
        return self.__default_emotion

