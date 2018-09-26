// Author: Nikolay Khokhlov <k_h@inbox.ru>, (C) 2013

#ifndef TRAIN_FUNCTION_H
#define TRAIN_FUNCTION_H

#include "core/function.h"

class TrainFunction : public BaseFunction {
public:
	DECLARE_CLASS_NAME(TrainFunction);
	TrainFunction();
	virtual ~TrainFunction();
	virtual vector1 value(const vector1& x, const real_t t);
	virtual vector2 value(const vector2& x, const real_t t);
	virtual vector3 value(const vector3& x, const real_t t);
	virtual real_t    value(const real_t& x,    const real_t t);
	virtual void setParams(kutils::ConfigEntry& ent);
protected:
	BaseImpulse *imp;
	vector3 velocity;
	vector3 force;
	real_t h;
	real_t l;
	real_t w;
	vector3 pos;

	real_t t_soft_half;

	int if_polzun;
	real_t h_polzun;
	real_t r_wheel;
	real_t cp_rail;
	real_t rho_rail;
	real_t height_rail;
	real_t eps;
	real_t dis_polzun;
	real_t J_rail;
	real_t F_norm;
};

#endif // TRAIN_FUNCTION_H
