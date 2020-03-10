import sys
import jenkins
import re

def get_projects(path):
    projects = []
    with open(path, 'r') as f:
        for line in f:
            project_name = line.strip()
            projects.append(project_name)

    return projects

def extract_test_data(test_report):

    if not test_report:
        return (None,None)

    test_duration = test_report['duration']

    # Get test specific data.
    test_cases_result = []

    #Each suite test a class
    for suite in test_report['suites']:

        class_structure = suite['name'].split('.')
        package = ".".join(class_structure[:-1])
        class_ = class_structure[-1]

        # Each case tests something different in a class
        for case in suite['cases']:
        
            test_cases_result.append([package, class_,case['name'],\
            case['duration'], case['status']])
    
    return (test_duration, test_cases_result)

def get_data(builds , server):
    
    builds_tests_data = []

    for build in builds:

        build_data = {}

        build_data['build_number'] = build['id']
        build_data['build_result'] = build['result']
        build_data['build_duration'] = build['duration']
        build_data['build_estimated_duration'] = build['estimatedDuration']

        # Get revision number
        revision_number = None

        for action in build['actions']:
            if not action:
                continue

            if action['_class'].split('.')[-1] == 'TestResultAction':
                fail_count = action['failCount']
                skip_count = action['skipCount']
                total_count = action['totalCount']

            if action['_class'].split('.')[-1] == 'BuildData':
                if 'lastBuiltRevision' in action:
                    if 'SHA1' in action['lastBuiltRevision']:
                        revision_number = action['lastBuiltRevision']['SHA1']

        build_data['build_revision_number'] = revision_number

        # Get info about commit
        commit_ids_ts = {}

        changeset_items = build['changeSet']['items']
        for item in changeset_items:
            if 'commitId' in item:
                if 'date' in item:
                    commit_ids_ts[item['commitId']] = item['date']
                else:
                    commit_ids_ts[item['commitId']] = None

        if len(commit_ids_ts) != 1:
            print(f"WARNING: {len(commit_ids_ts)} commits ids found for the build \
                {build['fullDisplayName']}")

        build_data['build_commit_ids_ts'] = commit_ids_ts

        # Get general test data:
        job_name = build['fullDisplayName'].split('#')[0].strip()
        test_report = server.get_build_test_report(job_name , int(build_data['build_number']), depth=0)

        if not test_report:
            print(f"WARNING: No test report for {job_name} - {build_data['build_number']}")
            build_data['failCount'] = None
            build_data['passCount'] = None
            build_data['skipCount'] = None
            build_data['totalTestDuration'] = None

            builds_tests_data.append((build_data, None))
            continue

        build_data['failCount'] = test_report['failCount']
        build_data['skipCount'] = test_report['skipCount']

        if 'passCount' in test_report:
            build_data['passCount'] = test_report['passCount']

        if 'totalCount' in test_report:
            build_data['passCount'] = test_report['totalCount'] - test_report['failCount'] - test_report['skipCount']

        # Get specific test data:
        total_test_duration = None
        test_result = []
        test_report_class = test_report['_class'].split('.')[-1]
        if test_report_class == "SurefireAggregatedReport":

            for child_report in test_report['childReports']:
                duration, child_test_result = extract_test_data(child_report['result'])
                if duration is not None:
                    if total_test_duration is None:
                        total_test_duration = duration
                    else:
                        total_test_duration += duration
                if child_test_result is not None:
                    test_result = test_result + child_test_result

        elif test_report_class == "TestResult":
            total_test_duration, test_result = extract_test_data(test_report)

        else:
            print(f"WARNING: Unrecognized test report class for {job_name} - {build_data['build_number']}")

        build_data['totalTestDuration'] = total_test_duration
        
        builds_tests_data.append((build_data, test_result))

    return builds_tests_data

def write_to_csv(project_info):
    pass

def process_project(project, server, sub_project=False):

    if sub_project:
        jobs_info = [server.get_job_info(project, depth=2)]
    else:
        regex = re.compile(f"^.*{project}.*$", re.IGNORECASE)

        # depth = 2 to extract some more info to avoid querying the server many times
        jobs_info = server.get_job_info_regex(regex, folder_depth=0, depth=2)

    project_info = {}

    for job_info in jobs_info:

        class_ = job_info['_class'].split('.')[-1]
        fullName = job_info['fullName']

        if class_ in ['Folder', 'OrganizationFolder', 'WorkflowMultiBranchProject']:
            # There should be a "jobs" field containing more jobs:
            # drill again using server.get_job_info(name, depth=2)
            # rather than doing regex again

            # process_project(server, job_info['jobs'], True)
            pass

        else:
            # 'scm' field is only available for these types of classes:
            if 'scm' in job_info and '_class' in job_info['scm']:

                scm_class = job_info['scm']['_class']
                if scm_class.split('.')[-1] in ['SubversionSCM','NullSCM']:
                    continue

            builds_data = get_data(job_info['builds'], server)
    
        #project_info[fullName] = (builds_data, test_data)
    
    #write_to_csv(project_info)

if __name__ == "__main__":

    server = jenkins.Jenkins('https://builds.apache.org/')

    # Sometimes connecting to Jenkins server is banned due to ill use of API
    # Test connection to server
    print(f"Jenkins-API version: {server.get_version()}")

    if len(sys.argv)  != 2:
        print("Provide also path to one csv file with projects' names in it.") 
        sys.exit(1)

    projects = get_projects(sys.argv[1])    
    print(projects)

    for project in projects:
        process_project(project, server)