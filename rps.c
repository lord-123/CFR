#include <stdio.h>
#include <stdlib.h>
#include <time.h>

enum ACTION
{
	ROCK,
	PAPER,
	SCISSORS,
	ACTION_C
};

double regret_sum[ACTION_C];
double strategy[ACTION_C];
double strategy_sum[ACTION_C];
double opp_strategy[] = { 0.4, 0.3, 0.3 };

double *get_strategy()
{
	double normalising_sum = 0;

	int a;
	for (a = 0; a < ACTION_C; ++a)
	{
		strategy[a] = regret_sum[a] > 0 ? regret_sum[a] : 0;
		normalising_sum += strategy[a];
	}

	for (a = 0; a < ACTION_C; ++a)
	{
		if (normalising_sum > 0)
			strategy[a] /= normalising_sum;
		else
			strategy[a] = 1.0 / ACTION_C;

		strategy_sum[a] += strategy[a];
	}

	return strategy;
}

double rand_double(double min, double max)
{
	double range = max - min;
	double div = RAND_MAX / range;
	return min + (rand() / div);
}

int get_action(double *strategy)
{
	double r = rand_double(0, 1);
	int a;
	double cum_prob = 0;

	for (a = 0; a < ACTION_C - 1; ++a)
	{
		cum_prob += strategy[a];
		if (r < cum_prob) break;
	}

	return a;
}

void train(int iterations)
{
	double action_util[ACTION_C];
	int i;

	for (i = 0; i < iterations; ++i)
	{
		// get regret-matched mix-strategy actions
		double *strategy = get_strategy();
		int our_action = get_action(strategy);
		int opp_action = get_action(opp_strategy);

		// compute action utilities
		action_util[opp_action] = 0;
		action_util[opp_action == ACTION_C - 1 ? 0 : opp_action + 1] =  1;
		action_util[opp_action == 0 ? ACTION_C - 1 : opp_action - 1] = -1;

		// accumulate action regrets
		int a;
		for (a = 0; a < ACTION_C; ++a)
			regret_sum[a] += action_util[a] - action_util[our_action];

		if (i % 100000 == 0) printf("i: %d\n", i);
	}
}

double *get_avg_strategy()
{
	double *avg_strategy = malloc(ACTION_C * sizeof(double));
	double normalising_sum = 0;
	int a;

	for (a = 0; a < ACTION_C; ++a)
		normalising_sum += strategy_sum[a];
	for (a = 0; a < ACTION_C; ++a)
		if (normalising_sum > 0)
			avg_strategy[a] = strategy_sum[a] / normalising_sum;
		else
			avg_strategy[a] = 1.0 / ACTION_C;

	return avg_strategy;
}

int main()
{
	train(100000000);
	double *avg_strategy = get_avg_strategy();

	int i;
	for (i = 0; i < ACTION_C; ++i)
		printf("%f ", avg_strategy[i]);
	putchar('\n');

	free(avg_strategy);
	avg_strategy = NULL;
}
