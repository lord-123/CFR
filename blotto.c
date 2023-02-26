#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define S 5
#define N 3

const int OPTIONS[][N] = {
{5, 0, 0}, {0, 5, 0}, {0, 0, 5},
{4, 1, 0}, {1, 4, 0}, {0, 4, 1}, {0, 1, 4}, {4, 0, 1}, {1, 0, 4},
{3, 2, 0}, {2, 3, 0}, {0, 3, 2}, {0, 2, 3}, {3, 0, 2}, {2, 0, 3},
{3, 1, 1}, {1, 3, 1}, {1, 1, 3},
{2, 2, 1}, {2, 1, 2}, {1, 2, 2}
};
#define OPTION_C (sizeof(OPTIONS)/(sizeof(int)*3))

double regret_sum[OPTION_C];
double strategy[OPTION_C];
double strategy_sum[OPTION_C];
//double opp_strategy[OPTION_C] = {0, 0, 1.0, 0};

double *get_strategy()
{
	double normalising_sum = 0;

	int a;
	for (a = 0; a < OPTION_C; ++a)
	{
		strategy[a] = regret_sum[a] > 0 ? regret_sum[a] : 0;
		normalising_sum += strategy[a];
	}

	for (a = 0; a < OPTION_C; ++a)
	{
		if (normalising_sum > 0)
			strategy[a] /= normalising_sum;
		else
			strategy[a] = 1.0 / OPTION_C;

		strategy_sum[a] += strategy[a];
	}

	return strategy;
}

double rand_double(double min, double max)
{
	double range = max-min;
	double div = RAND_MAX / range;
	return min + (rand() / div);
}

int get_action(double *strategy)
{
	double r = rand_double(0, 1);
	int a;
	double cum_prob = 0;

	for (a = 0; a < OPTION_C - 1; ++a)
	{
		cum_prob += strategy[a];
		if (r < cum_prob) break;
	}

	return a;
}

int utility(int s1, int s2)
{
	int i;
	int s1_count=0;
	int s2_count=0;

	for (i = 0; i < N; ++i)
	{
		if (OPTIONS[s1][i] > OPTIONS[s2][i]) ++s1_count;
		else if (OPTIONS[s1][i] < OPTIONS[s2][i]) ++s2_count;
	}

	if (s1_count == s2_count) return 0;
	return s1_count > s2_count ? 1 : -1;
}

void train(int iterations)
{
	int action_util[OPTION_C];
	int i;

	for (i = 0; i < iterations; ++i)
	{
		// get actions
		double *strategy = get_strategy();
		int p1_action = get_action(strategy);
		int p2_action = get_action(strategy);

		int a;
		for (a = 0; a < OPTION_C; ++a)
		{
			action_util[a] = utility(a, p2_action);
		}

		for (a = 0; a < OPTION_C; ++a)
		{
			regret_sum[a] += action_util[a] - action_util[p1_action];
		}

		if (i % 10000 == 0) printf("i: %d\n", i);
	}
}

double *get_avg_strategy()
{
	double *avg_strategy = malloc(OPTION_C * sizeof(double));
	double normalising_sum = 0;
	int a;

	for (a = 0; a < OPTION_C; ++a)
		normalising_sum += strategy_sum[a];
	for (a = 0; a < OPTION_C; ++a)
		if (normalising_sum > 0)
			avg_strategy[a] = strategy_sum[a] / normalising_sum;
		else
			avg_strategy[a] = 1.0 / OPTION_C;

	return avg_strategy;
}

int main()
{
	train(1000000);
	double *avg_strategy = get_avg_strategy();

	int i;
	int j;
	for (i = 0; i < OPTION_C; ++i)
	{
		printf("%f ", avg_strategy[i]);
		for (j = 0; j < N; ++j)
			printf("%d ", OPTIONS[i][j]);
		putchar('\n');
	}

	free(avg_strategy);
	avg_strategy = NULL;
}
