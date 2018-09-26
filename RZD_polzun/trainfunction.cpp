#include "elastic/trainfunction.h"

#include "core/geometry.h"

using namespace std;

REGISTER_BASE_DERIVED(BaseFunction, TrainFunction);

TrainFunction::TrainFunction()
{
}

TrainFunction::~TrainFunction()
{
}

vector1 TrainFunction::value(const vector1& x, const real_t t)
{
	return vector1(value(vector2(x.x, 0.0), t).x);
}

vector2 TrainFunction::value(const vector2& x, const real_t t)
{
	vector3 v = value(vector3(x.x, x.y, 0.0), t);
	return vector2(v.x, v.y);
}

vector3 TrainFunction::value(const vector3& x, const real_t t)
{
	vector3 f(0.0, 0.0, 0.0);
	vector3 n = velocity / norm(velocity);
	vector3 npos;
	real_t d;
	real_t koef_soft;
	real_t t_soft;
	int if_sqr = 0;

	real_t alpha_0;
	real_t alpha;
	real_t alpha_cr;
	real_t v_norm;
	real_t omega;
	real_t l_polzun;
	real_t t0;
	real_t t1;
	real_t t2;
	real_t t_soft_polzun;
	real_t w_right_half_new;
	real_t v_now;
	real_t koef_polzun;
	real_t force_norm;
	real_t beta;

	koef_soft = 1.0;
	t_soft = t/t_soft_half;
	npos = pos + velocity * (t-t_soft_half);

	if (if_sqr == 0) {
		if (t_soft<1.0){
			koef_soft = t_soft;
			npos = pos;
		}
	}

	d = dot(x, n) - dot(npos, n) - l / 2 - h / 2;
	if (if_polzun == 0) {
		if (std::abs(d) <= w / 2.0) {
			f = koef_soft * force * imp->val((w / 2.0 + d) / w);
		}
	}
	if (if_polzun == 1) {
		v_norm = sqrt(dot(velocity, velocity)); 
		alpha_0 = acos(1.0 - h_polzun/r_wheel);
		omega = (v_norm/r_wheel); //*(sin(alpha_0)/alpha_0);

		force_norm = sqrt(dot(force, force));
		beta = v_norm*F_norm/J_rail;
		l_polzun = 2.0*r_wheel*sin(alpha_0);

		t0 = t_soft_half + dis_polzun/v_norm;

		t1 = t0 + pow(6.0*alpha_0/beta, 1.0/3.0);
		alpha = alpha_0 - omega*(t1-t0) - beta*(t1-t0)*(t1-t0)*(t1-t0)/6.0;
		for ( ; std::abs(alpha) < (alpha_0/1000.0); ) {
			t1 = t1 + alpha/(omega + beta*(t1-t0)*(t1-t0)/2.0);
			alpha = alpha_0 - omega*(t1-t0) - beta*(t1-t0)*(t1-t0)*(t1-t0)/6.0;
		}

		t2 = t1 + alpha_0/omega;
		t_soft_polzun = 2.0*height_rail/cp_rail;

		if (t>t1) {
			if ((t-t1) >= t_soft_polzun) {
				koef_polzun = 1.0;
			}
			if ((t-t1) < t_soft_polzun) {
				v_now = l_polzun*(omega+beta*(t1-t0)*(t1-t0)/2.0);
				koef_polzun = cp_rail*rho_rail*v_now/force_norm;
				koef_polzun = koef_polzun * ( 1.0 - (t-t1)/t_soft_polzun );
				koef_polzun = 1.0 + koef_polzun;
			}
		}
		if (t>t2){
			if (std::abs(d) <= w / 2.0) {
				f = koef_polzun * koef_soft * force * imp->val((w / 2.0 + d) / w);
			}
		}
		if (t<t0){
			if (std::abs(d) <= w / 2.0) {
				f = koef_soft * force * imp->val((w / 2.0 + d) / w);
			}
		}
		else if (t<t1){
			alpha = alpha_0 - omega*(t-t0) - beta*(t-t0)*(t-t0)*(t-t0)/6.0;
			alpha_cr = atan(eps/l_polzun);

			w_right_half_new = l_polzun;
			if (alpha>alpha_cr) {
				w_right_half_new = eps/tan(alpha);
			}

			v_now = w_right_half_new*(omega+beta*(t-t0)*(t-t0)/2.0);
			koef_polzun = 1.0 + cp_rail*rho_rail*v_now/force_norm;

			if (w_right_half_new<=w) {
				if (std::abs(d) <= w / 2.0) {
					f = koef_polzun * force * imp->val((w / 2.0 + d) / w);
				}
			}

			if (w_right_half_new>w) {
				if (std::abs(d) <= (w_right_half_new / 2.0) ) {
					if (std::abs(d) <= (w_right_half_new/2.0 - w/2.0) ) {
						f = koef_polzun * force;
					}
					else {
						if (d>(w_right_half_new/2.0 - w/2.0) ) {
							f = koef_polzun * force * imp->val(( d - w_right_half_new/2.0 + w) / w);;
						}
						if (d<(w/2.0 - w_right_half_new/2.0) ) {
							f = koef_polzun * force * imp->val(( d + w_right_half_new/2.0 ) / w);;
						}
					}
				}
			}
		}
		else if (t<t2) {
			alpha = omega*(t-t1);
			alpha_cr = atan(eps/l_polzun);

			w_right_half_new = l_polzun;
			if (alpha>alpha_cr) {
				w_right_half_new = eps/tan(alpha);
			}

			if (w_right_half_new<=w) {
				if (std::abs(d) <= w / 2.0) {
					f = koef_polzun * force * imp->val((w / 2.0 + d) / w);
				}
			}

			if (w_right_half_new>w) {
				if (std::abs(d) <= (w_right_half_new / 2.0) ) {
					if (std::abs(d) <= (w_right_half_new/2.0 - w/2.0) ) {
						f = koef_polzun * force;
					}
					else {
						if (d>(w_right_half_new/2.0 - w/2.0) ) {
							f = koef_polzun * force * imp->val(( d - w_right_half_new/2.0 + w) / w);;
						}
						if (d<(w/2.0 - w_right_half_new/2.0) ) {
							f = koef_polzun * force * imp->val(( d + w_right_half_new/2.0 ) / w);;
						}
					}
				}
			}
		}
	}

	d = dot(x, n) - dot(npos, n) - l / 2 + h / 2;
	if (std::abs(d) <= w / 2.0) {
		f = koef_soft * force * imp->val((w / 2.0 + d) / w);
	}
	d = dot(x, n) - dot(npos, n) + l / 2 - h / 2;
	if (std::abs(d) <= w / 2.0) {
		f = koef_soft * force * imp->val((w / 2.0 + d) / w);
	}
	d = dot(x, n) - dot(npos, n) + l / 2 + h / 2;
	if (std::abs(d) <= w / 2.0) {
		f = koef_soft * force * imp->val((w / 2.0 + d) / w);
	}
	return f;
}

real_t TrainFunction::value(const real_t& x, const real_t t)
{
	return value(vector1(x), t).x;
}

void TrainFunction::setParams(kutils::ConfigEntry& ent)
{
	BaseFunction::setParams(ent);
	imp = ImpulseFactory::getInstance().create(ent.getEntry("impulse"));
	h = ent.get<real_t>("h");
	l = ent.get<real_t>("l");
	w = ent.get<real_t>("w");

	t_soft_half = ent.get<real_t>("t_soft_half");

	if_polzun = ent.get<int>("if_polzun");
	h_polzun = ent.get<real_t>("h_polzun");
	r_wheel = ent.get<real_t>("r_wheel");
	cp_rail = ent.get<real_t>("cp_rail");
	rho_rail = ent.get<real_t>("rho_rail");
	height_rail = ent.get<real_t>("height_rail");
	eps = ent.get<real_t>("eps");
	dis_polzun = ent.get<real_t>("dis_polzun");
	J_rail = ent.get<real_t>("J_rail");
	F_norm = ent.get<real_t>("F_norm");

	vector<double> t;
	ent.getEntry("velocity").getDoubleArray(t);
	RECT_ASSERT(t.size() <= 3, "TrainFunction::setParams: Invalid velocity size.");
	velocity.null();
	for (int i = 0; i < (int)t.size(); i++) {
		velocity.begin()[i] = t[i];
	}

	t.clear();
	ent.getEntry("pos").getDoubleArray(t);
	RECT_ASSERT(t.size() <= 3, "TrainFunction::setParams: Invalid pos size.");
	pos.null();
	for (int i = 0; i < (int)t.size(); i++) {
		pos.begin()[i] = t[i];
	}

	t.clear();
	ent.getEntry("force").getDoubleArray(t);
	RECT_ASSERT(t.size() <= 3, "TrainFunction::setParams: Invalid force size.");
	force.null();
	for (int i = 0; i < (int)t.size(); i++) {
		force.begin()[i] = t[i];
	}
}
