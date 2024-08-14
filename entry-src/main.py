"""
Cheng Ho Ming, Eric
This is my submission for the UBS Global Coding Challenge, Hong Kong Edition, 2024 in Python.

Assumptions:
* The JSON file is valid and not empty, and the schema is UTF-8 encoded.
* Python >=3.9 is used for this submission.
* If two students have the same weightage score for different schools,
    the student with a smaller numerical ID value will be selected to enroll
    in the school that appears first in the JSON file.
"""

# Required
import json
import sys
import re

# Optional
import dataclasses


@dataclasses.dataclass
class School:
    """
    Represents a school that students are applying to.
    """

    def __init__(self, name: str, location: list[int], maxAllocation: int) -> None:
        """
        Initializes a new instance of the class.

        Args:
            name (String): Uniquely identifies a school
            location (List of Integer): Coordinate of school location
            maxAllocation (Integer): Number of vacancies
        """
        self.name: str = name
        self.location: list[int] = location
        self.maxAllocation: int = maxAllocation

    def __dict__(self) -> dict:
        """
        Returns the dictionary representation of the object.

        Returns:
            Dictionary: Dictionary representation of the object
        """
        return {
            "name": self.name,
            "location": self.location,
            "maxAllocation": self.maxAllocation,
        }


class Student:
    """
    Represents a student who is applying to schools.
    """

    weightage_homeSchoolDistance: float = 0.5
    weightage_schoolAlumni: float = 0.3
    weightage_schoolVolunteer: float = 0.2

    def __init__(
        self,
        id: int,
        homeLocation: list[int],
        alumni: str = None,
        volunteer: str = None,
    ) -> None:
        """
        Initializes a new instance of the class.

        Args:
            id (Integer): Uniquely identifies a student
            homeLocation (List of Integer): Coordinate of home location
            alumni (String, optional): School Alumni
            volunteer (String, optional): School Volunteer
        """
        self.id: int = id
        self.homeLocation: list[int] = homeLocation
        self.alumni: str = alumni
        self.volunteer: str = volunteer

    def homeSchoolDistance(self, school: School) -> float:
        """
        Calculates the distance between the student's home location and the school location.
        Distance of home to school is based off the Euclidean distance between 2 points.
        Args:
            school (School): School object

        Returns:
            Floating point number: Distance between student's home location and the school location
        """
        x_euclidean: float = (self.homeLocation[0] - school.location[0]) ** 2
        y_euclidean: float = (self.homeLocation[1] - school.location[1]) ** 2
        return (x_euclidean + y_euclidean) ** 0.5

    def is_alumni(self, school: School) -> bool:
        """
        Checks if the student is an alumni of the school.
        Args:
            school (School): School object

        Returns:
            Boolean: True if student is an alumni of the school, False otherwise
        """
        return self.alumni == school.name

    def is_volunteer(self, school: School) -> bool:
        """
        Checks if the student is a volunteer of the school.
        Args:
            school (School): School object

        Returns:
            Boolean: True if student is a volunteer of the school, False otherwise
        """
        return self.volunteer == school.name

    def weightage_score(self, school: School) -> float:
        """
        Calculates the weightage score of the student based on the school.
        Args:
            school (School): School object

        Returns:
            Floating point number: Weightage score of the student
        """
        # Students living closer to the school will receive a higher score
        score: float = (
            1 / self.homeSchoolDistance(school)
        ) * self.weightage_homeSchoolDistance
        if self.is_alumni(school):
            score += self.weightage_schoolAlumni
        if self.is_volunteer(school):
            score += self.weightage_schoolVolunteer
        return score

    def __dict__(self) -> dict:
        """
        Returns the dictionary representation of the object.

        Returns:
            Dictionary: Dictionary representation of the object
        """
        return {
            "id": self.id,
            "homeLocation": self.homeLocation,
            "alumni": self.alumni,
            "volunteer": self.volunteer,
        }


def main(file_path: str) -> None:
    """
    Main function to read the JSON file, deserialize the JSON data as School and Student objects
    and allocate students to schools based on the weightage score.
    """
    with open(file_path) as fstream:
        json_data = json.load(fstream)

    # Deserializing the json data as School and Student objects
    schools: list[School] = [School(**school) for school in json_data["schools"]]
    students: list[Student] = [Student(**student) for student in json_data["students"]]

    # In a scenario where 2 students have the same weightage score,
    # student with a smaller numerical id value will be selected.
    result: dict[str, list[int]] = {}
    for school in schools:
        sorted_students = sorted(
            students,
            key=lambda student: (
                # Sorting based on weightage score in descending order
                -student.weightage_score(school),
                # In case of a tie, student with smaller id value will be selected
                student.id,
            ),
        )
        # Allocate students to the school based on the maxAllocation
        result[school.name] = [
            student.id for student in sorted_students[: school.maxAllocation]
        ]
        # Remove students who have been allocated to the school
        students = [s for s in students if s.id not in result[school.name]]

    # Serializing the result as a JSON object, indented with 2 spaces
    formattedResult: list[dict[str, list[int]]] = [
        {key: values} for key, values in result.items()
    ]
    indentedResult: str = json.dumps(formattedResult, indent=2)

    # Function to remove extra spaces within square brackets
    def repl_func(match: re.Match):
        return " ".join(match.group().split())

    # (?<=\[) is a positive lookbehind assertion that matches a left square bracket ([)
    #    before the desired pattern.

    # [^\[\]]+ matches one or more characters that are not square brackets
    #    ([^\[\]]is a negated character class).

    # (?=]) is a positive lookahead assertion that matches a right square bracket (])
    #    after the desired pattern.
    indentedResult = re.sub(r"(?<=\[)[^\[\]]+(?=])", repl_func, indentedResult)

    # Write the indented result to output.json
    with open("output.json", "w") as fstream:
        fstream.write(indentedResult)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <json_file>")
        sys.exit(1)

    json_file: str = sys.argv[1]
    main(json_file)
