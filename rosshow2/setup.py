from setuptools import find_packages
from setuptools import setup

package_name = 'rosshow2'

setup(
    name=package_name,
    version='2.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    author='Chris Lalancette',
    author_email='clalancette@openrobotics.org',
    maintainer='Chris Lalancette',
    maintainer_email='clalancette@openrobotics.org',
    keywords=['ROS'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approvied :: MIT',
        'Programming Language :: Python',
        'Topic :: ROS',
    ],
    description='rosshow2',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'rosshow2 = nodes.rosshow2:main',
        ],
    },
)
