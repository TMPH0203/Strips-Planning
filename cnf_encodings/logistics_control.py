# COMP3620/6320 Artificial Intelligence
# The Australian National University - 2023
# Authors: COMP3620 team

""" Student Details

    Student Name: Mingbo Liu
    Student ID: U7517737
    Email: u7517737@anu.edu.au
    Date: 06/06/2023
"""
from typing import Dict, List, Tuple

"""
    In this file you will implement some constraints which represent
    domain-specific control knowledge for the Logistics domain
    (benchmarks/logistics).

    These constraints will be used in addition to a standard flat encoding of
    the Logistics problem instances, without plan graph mutexes (which you are
    assumed to have completed while going through Exercises 1-6).

    Those constraints should make solving the problem easier. This may be at
    the cost of optimality. That is, your additional constraints may rule out
    some solutions to make planning easier -- for example, by restricting the
    way trucks and planes can move -- but they should preserve SOME solution
    (the problems might be very easy to solve if you added a contradiction, but
    wholly uninteresting!).

    Often control knowledge for planning problems is based on LTL (Linear
    Temporal Logic - https://en.wikipedia.org/wiki/Linear_temporal_logic) and
    you might get inspired by studying this.

    We do not expect you to implement an automatic compilation of arbitrary LTL
    into SAT, just some control knowledge rules for problems from the Logistics
    domain.

    As an example rule to get you started, you could assert that if a package
    was at its destination, then it cannot leave.

    That is you could iterate over the goal of the problem to find the
    propositions which talk about where the packages should end up and make
    some constraints asserting that if one of the corresponding fluents is true
    at step t then it must still be true at step t + 1

    You will be marked based on the correctness, inventiveness, and
    effectiveness of the control knowledge you devise.

    You should aim to make at least three different control rules. Feel free to
    leave (but comment out) rules which you abandon if you think they are
    interesting and want us to look at them.

    Use the flag "-e logistics" to select this encoding and the flag "-p false"
    to disable the plangraph mutexes.
"""


from strips_problem import Action, Proposition
from .basic import BasicEncoding
encoding_class = 'LogisticsEncoding'


class LogisticsEncoding(BasicEncoding):
    """ An encoding which extends BasicEncoding but adds control knowledge
        specific for the Logistics domain.
    """

################################################################################
#                You need to implement the following methods                   #
################################################################################

    def make_control_knowledge_variables(self, horizon: int) -> None:
        """ Make the variable for the problem.

            Use the function self.new_cnf_code(step, name, object) to make
            whatever codes for CNF variables you need to make your control
            knowledge for the Logistics problem.

            You can make variables which mean anything if you can think of
            constraints to make that enforce that meaning. As an example, if
            you were making control logic for the miconics domain, you might
            make variables which keep track if each passenger has ever
            been in an elevator and is now not.

            For a passenger p, and t > 0:
                was_boarded(p)@t <->
                    (-boarded(p)@t ^ (boarded(p)@t-1 v was_boarded(p)@t-1))

            For example, you might make a dictionary called
            self.was_boarded_at_t indexed by passenger names, where the values
            are lists where the ith index contains the cnf code for
            was_boarded(p)@i, which you got by calling self.new_cnf_code(i,
            f"was_boarded({was_boarded.passenger})", was_boarded).

            You can see here that this is using an object called was_boarded
            which has an attribute "passenger" as the object. This might not be
            the simplest way, you might wish to just use a string instead of a
            more complicated object. For example, self.new_cnf_code(i,
            f"was_boarded({passenger})", f"was_boarded({passenger})").

            You can then use these variables, along with the fluent and action
            variables to make your control knowledge.

            Note that the use of `make_control_knowledge_variables` is
            completely optional. You don't have to implement any code
            in this method. At the end of the day, the most important thing
            is to add new clauses in `make_control_knowledge`.
        """
        """ *** YOUR CODE HERE *** """
        # - at_destination(p) @ t

        # Create variables for specific control knowledge

        # Control knowledge 1: If a package is at its destination, it cannot change
        # proposition: If the package is at its destination
        self.at_destination_at_s: Dict[Proposition, List[int]] = {}  # Dictionary to store CNF codes for at_destination(p)@s
        for proposition in self.problem.goal:
            if proposition not in self.at_destination_at_s.keys():
                self.at_destination_at_s[proposition] = []
            for step in range(horizon):
                code = self.new_cnf_code(step, f"at_destination({proposition})", proposition)
                self.at_destination_at_s[proposition].append(code)

        # Control knowledge 2: If a package is at its destination city, it cannot fly
        # proposition: If a package is at its destination city.
        self.at_destination_city: Dict[Tuple[str, str], List[int]] = {}
        packages = []
        destiny_cities = []
        for destiny_proposition in self.problem.propositions:
            if destiny_proposition in self.problem.goal:
                packages.append(destiny_proposition.variables[0])
                destiny_cities.append(destiny_proposition.variables[1])
        for i in range(len(packages)):
            package = packages[i]
            destiny_city = destiny_cities[i]
            for proposition in self.problem.propositions:
                if package in proposition.variables and destiny_city in proposition.variables and proposition.name == "at":
                    if (package, destiny_city) not in self.at_destination_city.keys():
                        self.at_destination_city[package, destiny_city] = []
                    for step in range(horizon):
                        code = self.new_cnf_code(step, f"at_destination_city({package}, {destiny_city})", f"at_destination_city({package}, {destiny_city})")
                        self.at_destination_city[package, destiny_city].append(code)

    def make_control_knowledge(self, horizon: int) -> None:
        """ This is where you should make your control knowledge clauses.

            These clauses should have the type "control".
        """

        """ *** YOUR CODE HERE *** """
        # Add clauses for specific control knowledge

        # Control knowledge 1: If a package is at its destination, it cannot leave
        # roughly 10% time decreased
        for package, codes in self.at_destination_at_s.items():
            for step in range(1, horizon):
                f1_val = codes[step - 1]
                f2_val = codes[step]
                clause = [-f1_val, f2_val]
                self.add_clause(clause, "control")

        # # Control knowledge 2: If a package is at its destination city, it cannot fly
        # for key, codes in self.at_destination_city.items():
        #     for step in range(0, horizon):
        #         f_val = codes[step]
        #         package = key[0]
        #         for action in self.problem.actions:
        #             for action_step in range(step, horizon):
        #                 if action.name == "LOAD-AIRPLANE" and package in action.parameters:
        #                     a_val = self.action_fluent_codes[(action, action_step)]
        #                     clause_2 = [-f_val, -a_val]
        #                     self.add_clause(clause_2, "control")

        # Control knowledge 3: If a carrier is just loaded, it has to move:
        for action_1 in self.problem.actions:
            if "LOAD" in action_1.name:
                carrier = action_1.parameters[1]
                for action_2 in self.problem.actions:
                    # if "UNLOAD" in action_2.name and carrier in action_2.parameters:
                    #     for step in range(1, horizon):
                    #         a1_val = self.action_fluent_codes[(action_1, step - 1)]
                    #         a2_val = self.action_fluent_codes[(action_2, step)]
                    #         clause_3 = [-a1_val, -a2_val]
                    #         self.add_clause(clause_3, "control")
                    if "FLY" in action_2.name or "DRIVE" in action_2.name and carrier in action_2.parameters:
                        for step in range(1, horizon):
                            a1_val = self.action_fluent_codes[(action_1, step - 1)]
                            a2_val = self.action_fluent_codes[(action_2, step)]
                            clause_3 = [-a1_val, a2_val]
                            self.add_clause(clause_3, "control")

        # Control knowledge 4: If a carrier is just move, and something's in it, it has to unload.
        for action_1 in self.problem.actions:
            if "FLY" or "DRIVE" in action_1.name:
                carrier = action_1.parameters[0]
                for action_2 in self.problem.actions:
                    if "UNLOAD" in action_2.name and carrier in action_2.parameters:
                        for step in range(1, horizon):
                            a1_val = self.action_fluent_codes[(action_1, step - 1)]
                            a2_val = self.action_fluent_codes[(action_2, step)]
                            for proposition in self.problem.propositions:
                                if proposition.name == "in" and carrier in proposition.variables:
                                    p_val = self.proposition_fluent_codes[(proposition, step)]
                                    clause_4 = [-a1_val, a2_val]
                                    clause_5 = [-p_val, a2_val]
                                    self.add_clause(clause_4, "control")
                                    self.add_clause(clause_5, "control")


################################################################################
#                    Do not change the following method                        #
################################################################################

    def encode(self, horizon, exec_semantics, plangraph_constraints):
        """ Make an encoding of self.problem for the given horizon.

            For this encoding, we have broken this method up into a number
            of sub-methods that you need to implement.

           (LogisticsEncoding, int, str, str) -> None
        """
        super().encode(horizon, exec_semantics, plangraph_constraints)
        self.make_control_knowledge_variables(horizon)
        self.make_control_knowledge(horizon)
