class PIDController:
    def __init__(self):
    	self.kp = 0.05
    	self.ki = 0.0001
    	self.kd = 1.5

    	self.p_error = 0
    	self.i_error = 0
    	self.d_error = 0


    def update(self, cte):
    	self.i_error += cte
    	self.d_error = cte - self.p_error
    	self.p_error = cte

    	return -(self.kp * self.p_error + self.ki * self.i_error + self.kd * self.d_error)
