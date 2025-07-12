from deap import base, creator, tools
import random

def run_genetic_algorithm(agente, n_baldozas=200, pop_size=10, ngen=5):

    n_acciones = len(agente.actions)

    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMax)

    toolbox = base.Toolbox()
    toolbox.register("attr_action", random.randint, 0, n_acciones - 1)
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_action, n_baldozas)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    def eval_individual(individual):
        # Ejecuta simulación y obtiene puntaje (e.g., x_pos)
        results = agente.make_results(individual)
        score = results["x_pos"]

        # Penaliza si muere o hay error
        if results["status"] == "dead":
            score -= 100
        if results["status"] == "error":
            score -= 500

        return (score,)

    toolbox.register("evaluate", eval_individual)
    toolbox.register("mate", tools.cxOnePoint)
    toolbox.register("mutate", tools.mutUniformInt, low=0, up=n_acciones - 1, indpb=0.05)
    toolbox.register("select", tools.selTournament, tournsize=3)


    pop = toolbox.population(n=pop_size)

    #evolucion
    for gen in range(ngen):
        offspring = toolbox.select(pop, len(pop))
        offspring = list(map(toolbox.clone, offspring))

        for c1, c2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < 0.7:
                toolbox.mate(c1, c2)
                del c1.fitness.values
                del c2.fitness.values

        for mut in offspring:
            if random.random() < 0.2:
                toolbox.mutate(mut)
                del mut.fitness.values

        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        pop[:] = offspring

    best_ind = tools.selBest(pop, 1)[0]
    return list(best_ind)
