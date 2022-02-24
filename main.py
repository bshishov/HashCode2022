from typing import List, Tuple, Set, Iterable, Dict, Optional
from attr import dataclass, attrib
from collections import defaultdict
import random

Skill = Tuple[str, int]


@dataclass(slots=True, hash=True, eq=True)
class Contributor:
    name: str
    skills: List[Skill] = attrib(hash=False, eq=False)
    skills_dict: Dict[str, int] = attrib(factory=lambda: defaultdict(int), hash=False, eq=False)

    def __attrs_post_init__(self):
        for s, level in self.skills:
            self.skills_dict[s] = level

    def up(self, skill: str):
        self.skills_dict[skill] += 1


@dataclass(slots=True)
class Project:
    name: str
    days: int
    score: int
    best_before: int
    roles: List[Skill]


@dataclass(slots=True)
class ResultProject:
    project: Project
    contribs: List[Contributor] = attrib(factory=set)


def write_results_to(results: List[ResultProject], f):
    f.write(str(len(results)))
    f.write("\n")
    for r in results:
        f.write(r.project.name)
        f.write("\n")
        f.write(" ".join([c.name for c in r.contribs]))
        f.write("\n")


def find_contributor_with_skill(
        contributors: Iterable[Contributor],
        skill: str,
        level: int,
        selected: List[Contributor]
) -> Optional[Contributor]:
    candidates = []
    for c in contributors:
        if c.skills_dict[skill] >= level and c not in selected:
            #n_skills = len(c.skills)
            #candidates.append((c, c.skills_dict[skill]))
            #candidates.append((c, -n_skills))
            candidates.append(c)

    if candidates:
        #c, _ = list(sorted(candidates, key=lambda c: c[1]))[0]
        #return c
        return random.choice(candidates)

    return None


def select_contribs_for(project: Project):
    pass


def solve(contributors: Dict[str, Contributor], projects: Dict[str, Project]) -> List[ResultProject]:
    projects = list(projects.values())

    #projects = list(sorted(projects, key=lambda p: p.score / p.days))  # по удельному скору
    #projects = list(sorted(projects, key=lambda p: (p.best_before, -p.score)))  # по дедлайну
    projects = list(sorted(projects, key=lambda p: (len(p.roles), p.best_before)))
    #projects = list(sorted(projects, key=lambda p: (p.best_before // 1000, p.score / p.days)))  # по дедлайну
    #random.shuffle(projects)

    results = []

    retries = defaultdict(int)

    while projects:
        project = projects.pop()
        selected_contribs = []

        for role_skill, role_level in project.roles:
            mentor = None
            contributor = None

            for potential_mentor in selected_contribs:
                if potential_mentor.skills_dict[role_skill] >= role_level:
                    mentor = potential_mentor
                    break

            if mentor:
                contributor = find_contributor_with_skill(contributors.values(), role_skill, role_level - 1, selected_contribs)

            if not contributor:
                contributor = find_contributor_with_skill(contributors.values(), role_skill, role_level, selected_contribs)

            if contributor:
                selected_contribs.append(contributor)

        if len(selected_contribs) == len(project.roles):
            for c, (role_skill, role_level) in zip(selected_contribs, project.roles):
                if c.skills_dict[role_skill] <= role_level:
                    c.up(role_skill)

            results.append(ResultProject(project, selected_contribs))
        else:
            if retries[project.name] < 5:
                projects.insert(1, project)
                retries[project.name] += 1

    return results


def main(filename: str):
    with open(filename) as f:
        n_contributors, n_projects = tuple(map(int, f.readline().split()))

        contribs = {}

        for _ in range(n_contributors):
            name, n_skills = f.readline().split()
            n_skills = int(n_skills)

            skills = []
            for _ in range(n_skills):
                skill, level = f.readline().split()
                level = int(level)
                skills.append((skill, level))

            contribs[name] = Contributor(name, skills)

        projects = {}
        for _ in range(n_projects):
            name, days, score, best_before, n_roles = f.readline().split()
            days, score, best_before, n_roles = int(days), int(score), int(best_before), int(n_roles)

            roles = []
            for _ in range(n_roles):
                skill, level = f.readline().split()
                level = int(level)
                roles.append((skill, level))

            projects[name] = Project(name, days, score, best_before, roles)

    results = solve(contribs, projects)

    with open(filename + ".out.txt", "w") as f:
        write_results_to(results, f)

    print(filename + " DONE!")


if __name__ == '__main__':
    from multiprocessing import Pool
    pool = Pool()
    with Pool(5) as p:
        print(p.map(main, [
            "b_better_start_small.in.txt",
            "c_collaboration.in.txt",
            "d_dense_schedule.in.txt",
            "e_exceptional_skills.in.txt",
            "f_find_great_mentors.in.txt",
        ]))

    #main("b_better_start_small.in.txt")
    #main("c_collaboration.in.txt")
    #main("d_dense_schedule.in.txt")
    #main("e_exceptional_skills.in.txt")
    #main("f_find_great_mentors.in.txt")
